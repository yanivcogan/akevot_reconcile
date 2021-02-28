app.controller('singleDoc', ['$scope', '$stateParams', '$rootScope', '$state', 'server',
function($scope, $stateParams, $rootScope, $state, server) {
	$scope.objectKeys = (a)=>Object.keys(a).filter(x=>["$$hashKey", "isFocused"].indexOf(x)===-1);
	$scope.focusedBlock = null;
	$scope.currentDocument = 0;
	$scope.tags = ["תשתיות", "אכיפת חוק", "פשעים","מינויי לתפקיד","השתלטות על שטחים"];
	$scope.currTag = {};
	$scope.selectedTags = [];
	$scope.document = {};
	$scope.docStatusOptions = [
		{val:"PENDING", label:"חדש"},
		{val:"FINISHED", label:"הושלם"},
		{val:"INPROGRESS", label:"נותרה עבודה"}
	]
	//the "title" attribute is the second in the array
	$scope.title_index = 1;
	server.requestPhp({id: $stateParams["docId"]}, 'get_doc').then(function (data) {
		$scope.document.data = JSON.parse(data.json);
		$scope.document.status = data.status === "PENDING" ? "FINISHED" : data.status;
	});
	$scope.setBlockFocus=function(q, b){
		$scope.unsetBlockFocus();
		$scope.focusedBlock={q:q, b:b};
		$scope.document.data.annotations[q].reconciled[b].isFocused=true;
	}
	$scope.unsetBlockFocus=function(q, b){
		if($scope.focusedBlock){
			let old = $scope.focusedBlock;
			try{
			$scope.document.data.annotations[old.q].reconciled[old.b].isFocused=false;
			}catch(err){}
		}
		$scope.focusedBlock=null;
	}
	$scope.isBlockFocus=function(q, b){
		return
			$scope.focusedBlock.q === q &&
			$scope.focusedBlock.b === b;
	}
	$scope.onAnswerBlockClick=function(){
		
	}
	$scope.transferProperty=function(u, q, a, key, $event){
		let focused = $scope.focusedBlock
		$scope.document.data.annotations[focused.q].reconciled[focused.b][key]=
		$scope.document.data.annotations[q].answers[u].answers[a].ans[key];
		$scope.unsetBlockFocus();
		if($event){
			$event.stopPropagation();
		}
	}
	$scope.commitBlock=function(k, a){
		$scope.document.data.annotations[k].reconciled.push(JSON.parse(JSON.stringify(a.ans)));
	}
	$scope.oncommittedBlockKeyup=function($event, q, a){
		if($event && $event.keyCode===46){
			if($scope.document.data.annotations[q].reconciled[a].isFocused){
				$scope.document.data.annotations[q].reconciled.splice(a, 1);
				$scope.unsetBlockFocus();
			}
		}
	}
	$scope.isCommitted=function(q, a, key){
		const relevantAnswers = q.reconciled.filter(ans=>ans[key].trim()===a[key].trim());
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
	$scope.saveDoc=function(){
		if($scope.saveInProgress){
			return;
		}
		let title = $scope.document.data.annotations[$scope.title_index].reconciled[0].title;
		let json = JSON.stringify($scope.document.data);
		let status = $scope.document.status;
		$scope.saveInProgress = true;
		server.requestPhp({id: $stateParams["docId"], title, json, status}, 'save_doc').then(function (data) {
			$scope.saveInProgress = false;
			alert("נשמר!");
		});
	}
}]);