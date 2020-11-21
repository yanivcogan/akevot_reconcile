app.controller('singleDoc', ['$scope', '$stateParams', '$rootScope', '$state', 'server',
function($scope, $stateParams, $rootScope, $state, server) {
	$scope.objectKeys = (a)=>Object.keys(a).filter(x=>["$$hashKey", "isFocused"].indexOf(x)===-1);
	$scope.focusedBlock = null;
	$scope.currentDocument = 0;
	$scope.tags = ["תשתיות", "אכיפת חוק", "פשעים","מינויי לתפקיד","השתלטות על שטחים"];
	$scope.currTag = {};
	$scope.selectedTags = [];
	$scope.documents = [];
	server.requestPhp({id: $stateParams["docId"]}, 'get_doc').then(function (data) {
		$scope.documents.push(JSON.parse(data.json));
		debugger;
	});
	$scope.setBlockFocus=function(d, q, b){
		$scope.unsetBlockFocus();
		$scope.focusedBlock={d:d, q:q, b:b};
		$scope.documents[d].annotations[q].reconciled[b].isFocused=true;
	}
	$scope.unsetBlockFocus=function(d, q, b){
		if($scope.focusedBlock){
			let old = $scope.focusedBlock;
			try{
			$scope.documents[old.d].annotations[old.q].reconciled[old.b].isFocused=false;
			}catch(err){}
		}
		$scope.focusedBlock=null;
	}
	$scope.isBlockFocus=function(d, q, b){
		return
			$scope.focusedBlock.d === d &&
			$scope.focusedBlock.q === q &&
			$scope.focusedBlock.b === b;
	}
	$scope.onAnswerBlockClick=function(){
		
	}
	$scope.transferProperty=function(u, q, a, key, $event){
		let focused = $scope.focusedBlock
		$scope.documents[focused.d].annotations[focused.q].reconciled[focused.b][key]=
		$scope.documents[focused.d].annotations[q].answers[u].answers[a][key];
		$scope.unsetBlockFocus();
		if($event){
			$event.stopPropagation();
		}
	}
	$scope.commitBlock=function(d, k, a){
		$scope.documents[d].annotations[k].reconciled.push(JSON.parse(JSON.stringify(a)));
	}
	$scope.oncommittedBlockKeyup=function($event, d, q, a){
		if($event && $event.keyCode===46){
			if($scope.documents[d].annotations[q].reconciled[a].isFocused){
				$scope.documents[d].annotations[q].reconciled.splice(a, 1);
				$scope.unsetBlockFocus();
			}
		}
	}
	$scope.isCommitted=function(q, a, key){
		const relevantAnswers = q.reconciled.filter(ans=>ans[key]===a[key]);
		return relevantAnswers.length;
	}
	$scope.addTag=function(){
		if($scope.selectedTags.indexOf($scope.currTag.name)!==-1)
			return;
		$scope.selectedTags.push($scope.currTag.name);
		$scope.currTag={};
	}
	$scope.removeTag=function(i){
		$scope.selectedTags.splice(i, 1);
	}
}]);