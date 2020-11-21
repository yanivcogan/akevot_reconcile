<?php
header('Content-Type: application/json');
header("Access-Control-Allow-Origin: *");
header("Access-Control-Allow-Headers: Content-Type");
date_default_timezone_set("Asia/Jerusalem");


define ('SERVERROOT',__DIR__);
date_default_timezone_set('UTC');
require SERVERROOT."/db.php";

$time = $_SERVER['REQUEST_TIME'];
$type = isset($_GET["type"]) ? $_GET["type"] : null;
$data = new StdClass;
$data = json_decode(file_get_contents("php://input"));

error_reporting(E_ALL);
ini_set("log_errors", 1);

$db = new Db("localhost","document_reconciliation","root","","");

switch ($type) {
	case "list_docs" :
		$raised = $data->raised;
		$unraised = $data->unraised;
		$params = array();
		$query = "
			SELECT docs.id, docs.title
			FROM docs
			LEFT JOIN (
				SELECT d.id AS id, count(f.id) AS count
				FROM docs AS d
				LEFT JOIN flags AS f ON f.doc_id = d.id";
		if(count($raised) > 0){
		$query.="
			WHERE f.flag IN (";
			for($i = 0; $i < count($raised); $i++){
				$query .= ":flag_".$i;
				if($i < count($raised) - 1){
					$query .= ", ";
				}
				$params["flag_".$i] = $raised[$i];
			}
			$query.=")";
		}
		$query.="
				GROUP BY d.id
			) AS raised_flags ON docs.id = raised_flags.id
			LEFT JOIN (
				SELECT d.id AS id, count(f.id) AS count
				FROM docs AS d
				LEFT JOIN flags AS f ON f.doc_id = d.id";
		if(count($unraised) > 0){
			$query.="
				WHERE f.flag IN (";
			for($i = 0; $i < count($unraised); $i++){
				$query .= ":unflag_".$i;
				if($i < count($unraised) - 1){
					$query .= ", ";
				}
				$params["unflag_".$i] = $unraised[$i];
			}
			$query.=")";
		}
		$query.="
				GROUP BY d.id
			) AS unraised_flags ON docs.id = unraised_flags.id
			WHERE
				(".(count($raised) > 0 ? "FALSE" : "TRUE") ." OR raised_flags.count > 0) AND
				(".(count($unraised) > 0 ? "FALSE" : "TRUE") ." OR (IFNULL(unraised_flags.count, 0) < 1))";
		
		$ans = $db->smartQuery(array(
			'sql' => $query,
			'par' => $params,
			'ret' => 'all'
		));
		break;
	case "get_doc" :
		$ans = $db->smartQuery(array(
			'sql' => "SELECT id, title, original_json AS json FROM docs WHERE id = :id",
			'par' => array('id' => ($data->id)),
			'ret' => 'assoc'
		));
		break;
}
echo json_encode($ans);