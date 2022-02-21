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
	case "flag_count" :
		$ans = $db->smartQuery(array(
			'sql' => "
			SELECT f.flag, d.status, COUNT(DISTINCT f.doc_id) AS count
			FROM flags AS f
			LEFT JOIN docs AS d ON f.doc_id = d.id
			GROUP BY f.flag, d.status
			",
			'par' => array(),
			'ret' => 'all'
		));
		break;
	case "list_docs" :
		$raised = $data->raised;
		$unraised = $data->unraised;
		$statuses = $data->statuses;
		$search = $data->search;
		$params = array();
		$query = "
			SELECT docs.id, docs.title,IFNULL(adjusted_json, original_json) AS json
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
		if(count($statuses) > 0){
			$query.=" AND
					docs.status IN (";
			for($i = 0; $i < count($statuses); $i++){
				$query .= ":status_".$i;
				if($i < count($statuses) - 1){
					$query .= ", ";
				}
				$params["status_".$i] = $statuses[$i];
			}
			$query.=")";
		}
		
		$docs = $db->smartQuery(array(
			'sql' => $query,
			'par' => $params,
			'ret' => 'all'
		));
		$ans = array();
		$search_params = explode(" ", $search);
		for($i = 0; $i < count($docs); $i++){
			$doc = json_encode(json_decode($docs[$i]["json"]), JSON_UNESCAPED_UNICODE );
			$include_doc = true;
			foreach ($search_params as $key => $term){
				if($term && strlen($term) && !strpos($doc, $term)){
					$include_doc = false;
				}
			}
			if($include_doc){
				$doc_res = array("id" => $docs[$i]["id"],"title" => $docs[$i]["title"]);
				array_push($ans, $doc_res);
			}
		}
		break;
	case "get_doc" :
		$ans = $db->smartQuery(array(
			'sql' => "SELECT id, title, original_json, status, IFNULL(adjusted_json, original_json) AS json FROM docs WHERE id = :id",
			'par' => array('id' => ($data->id)),
			'ret' => 'assoc'
		));

		$tags = $db->smartQuery(array(
			'sql' => "SELECT t.tag FROM doc_tags AS dt JOIN tags AS t on dt.tag_id = t.id WHERE dt.doc_id=:id",
			'par' => array('id' => ($data->id)),
			'ret' => 'all'
		));
		$ans["tags"] = $tags;
		break;
	case "save_doc" :
		$ans = $db->smartQuery(array(
			'sql' => "UPDATE docs
			SET title = :title, adjusted_json = :json, status = :status
			WHERE id = :id",
			'par' => array('id' => ($data->id),'json' => ($data->json),'status' => ($data->status),'title' => ($data->title)),
			'ret' => 'res'
		));
		/* save tags */
		/* empty existing list of tags associated with the document */
		$ans = $db->smartQuery(array(
			'sql' => "DELETE FROM doc_tags WHERE doc_id = :id",
			'par' => array('id' => ($data->id)),
			'ret' => 'res'
		));
		if(count($data->selectedTags) <= 0){
		    break;
		}
		/* save new tags to tag table */
		$updateTagList = "INSERT IGNORE INTO tags (tag) VALUES ";
		$tags = array();
		foreach ($data->selectedTags as $key => $tag){
		    $tags["tag_".$key] = $tag;
		    $updateTagList .= "(:tag_".$key.")";
		    if($key < count($data->selectedTags) - 1){
		        $updateTagList .= ", ";
		    }
        }
		$tags = $db->smartQuery(array(
                			'sql' => $updateTagList,
                			'par' => $tags,
                			'ret' => 'all'
                		));
        /* get ids of all relevant tags */
        $getTagIds = "SELECT id FROM tags WHERE tag in(";
        $tags = array();
        foreach ($data->selectedTags as $key => $tag){
            $tags["tag_".$key] = $tag;
            $getTagIds .= ":tag_".$key."";
            if($key < count($data->selectedTags) - 1){
        		$getTagIds .= ", ";
        	}
        }
        $getTagIds .= ")";
        $tags = $db->smartQuery(array(
                        			'sql' => $getTagIds,
                        			'par' => $tags,
                        			'ret' => 'all'
                        		));
        $insertDocTags = "INSERT INTO doc_tags (doc_id, tag_id) VALUES ";
        $params = array("doc_id" => ($data->id));
        foreach ($tags as $key => $tag){
            $params["tag_".$key] = $tag["id"];
            $insertDocTags .= "(:doc_id, :tag_".$key.")";
            if($key < count($tags) - 1){
        		$insertDocTags .= ", ";
        	}
        }
        $tags = $db->smartQuery(array(
                        			'sql' => $insertDocTags,
                        			'par' => $params,
                        			'ret' => 'res'
                        		));
		break;
	case "get_tags" :
		$ans = $db->smartQuery(array(
			'sql' => "SELECT id, tag FROM tags",
			'par' => array(),
			'ret' => 'all'
		));
		break;

	case "export_docs" :
    	$ans = $db->smartQuery(array(
    		'sql' => "SELECT id, title, status, IFNULL(adjusted_json, original_json) AS json FROM docs",
    		'par' => array('id' => ($data->id)),
    		'ret' => 'all'
    	));
        break;
}
echo json_encode($ans);