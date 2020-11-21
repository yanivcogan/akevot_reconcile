<?php
//http://codereview.stackexchange.com/questions/602/database-class-using-pdo

/* Operate on the database using our super-safe PDO system */
class Db
{
    /* PDO istance */
    private $db = NULL;
    /* Number of the errors occurred */
    private $errorNO = 0;
	/* the kast DB error*/
	private $lastError=null;
	
	private $logFilePath;

    /* Connect to the database, no db? no party */
    public function __construct($host,$name,$user,$pass,$logFilePath)
    {
        try
        {
            $this->db = new PDO('mysql:dbname='.$name.';host='.$host, $user, $pass,array(PDO::MYSQL_ATTR_INIT_COMMAND => "SET NAMES utf8"));
			$this->logFilePath=$logFilePath;
        }
        catch (Exception $e) 
        {
            exit('DB shoutdown '.$e);
        }
    }

    /* Have you seen any errors recently? */
    public function getErrors() { return ($this->errorNO > 0) ? $this->errorNO : false; }
	
	/* get last error aray data */
	public function getLastError() { return $this->lastError;}

    /* Perform a full-control query */
    public function smartQuery($array)
    {
        # Managing passed vars
        $sql = $array['sql'];
        $par = (isset($array['par'])) ? $array['par'] : array();
        $ret = (isset($array['ret'])) ? $array['ret'] : 'res';

        # Executing our query
        $obj = $this->db->prepare($sql);
		
		foreach($par as $key=>&$value){		
			switch (gettype($value)){
				case "integer":
					$obj->bindParam($key, $value, PDO::PARAM_INT);
					break;
				case "string":
					$obj->bindParam($key, $value, PDO::PARAM_STR);
					break;
				case "boolean":
					$obj->bindParam($key, $value, PDO::PARAM_BOOL);
					break;
				case "NULL":
					$obj->bindParam($key, $value, PDO::PARAM_NULL);
					break;
				case "Object":
				case "array":
					$value=json_encode($value);
					$obj->bindParam($key, $value, PDO::PARAM_STR);
					break;
				default:
					$obj->bindParam($key, $value, PDO::PARAM_STR);
			}
		}

		$result = $obj->execute();
		//$result = $obj->execute($par);

        # Error occurred...
        if (!$result) 
		{ 
			$this->sqlErrorHandle($obj->errorInfo(),$sql,$par);
		}

        # What do you want me to return?
        switch ($ret)
        {
            case 'obj':
            case 'object':
                return $obj;
            break;

            case 'ass':
            case 'assoc':
            case 'fetch-assoc':
                return $obj->fetch(PDO::FETCH_ASSOC);
            break;

            case 'all':
            case 'fetch-all':
                return $obj->fetchAll(PDO::FETCH_ASSOC); // PDO::FETCH_ASSOC will remove the numeric index of the result.
            break;

            case 'res':
            case 'result':
                return $result;
			break;
			case 'count':
                return $obj->rowCount();
            break;

            default:
                return $result;
            break;
        }
    }
	
	/* handel error and save data in log fiile */
	private function sqlErrorHandle($errorInfo,$sql,$par){
		++$this->errorNO;
		$this->lastError=$errorInfo;
		$errorInfo[]=$sql;
		$errorInfo[]=$par;
		$errorInfo[]=date("Y-m-d H:i:s"); 				
		$line = json_encode($errorInfo)."\n";
		echo( $line );
		//file_put_contents($this->logFilePath, $line, FILE_APPEND | LOCK_EX);
		//print_r($line);
	}
	
	/* returnn the last Insert ID */
	public function getLastInsertId(){
		return $this->db->lastInsertId();
	}
	
	/* returnn the last Insert ID */
	public function getUUID(){
		$myuuid = $this->smartQuery(array(
				'sql' => "select UUID() as uuid",
					'par' => array(),
					'ret' => 'fetch-assoc'
				));
		return $myuuid['uuid'];
	}
	
    /* Get PDO istance to use it outside this class */
    public function getPdo() { return $this->db; }

    /* Disconnect from the database */
    public function __destruct() { $this->db = NULL; }
}