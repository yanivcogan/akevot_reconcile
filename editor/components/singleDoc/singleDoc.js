app.controller('singleDoc', ['$scope', '$stateParams', '$rootScope', '$state', 'server', 'imageIndex',
function($scope, $stateParams, $rootScope, $state, server, imageIndex) {
	$scope.objectKeys = (a)=>Object.keys(a).filter(x=>["$$hashKey", "isFocused"].indexOf(x)===-1);
	$scope.focusedBlock = {};
	$scope.currentDocument = 0;
	$scope.tags = ["תשתיות", "אכיפת חוק", "פשעים","מינויי לתפקיד","השתלטות על שטחים"];
	$scope.currTag = {};
	$scope.selectedTags = [];
	$scope.document = {};
	$scope.docStatusOptions = [
		{val:"PENDING", label:"חדש"},
		{val:"FINISHED", label:"הושלם"},
		{val:"INPROGRESS", label:"נותרה עבודה"}
	];
	$scope.textareaFields = new Set(["summary", "title"]);
	//the "title" attribute is the second in the array
	$scope.title_index = 1;
	$scope.docId = $stateParams["docId"];


	$scope.pages = imageIndex.getPages($stateParams["docId"]);
	$scope.currPage = 0;
	$scope.imgControls = {brightness: 100, contrast: 100, saturation: 100}


	$scope.saveInProgress = false;
	$scope.saveSuccessful = false;

	server.requestPhp({id: $scope.docId}, 'get_doc').then(function (data) {
		$scope.document.data = JSON.parse(data.json);
		$scope.document.status = data.status === "PENDING" ? "FINISHED" : data.status;
		window.setTimeout(()=>{
			document.querySelectorAll("textarea.property-input").forEach(x=>{
				x.dispatchEvent(new Event('input', { bubbles: true }))
			})
		}, 1000)
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
			$scope.document.data.annotations[old.q].reconciled[old.b].isFocused=null;
			}catch(err){}
		}
		$scope.focusedBlock=null;
	}
	$scope.unsetAllFocus=function(){
		for(let i = 0; i < $scope.document.data.annotations.length; i++){
			for(let j = 0; j < $scope.document.data.annotations[i].reconciled.length; j++){
				$scope.document.data.annotations[i].reconciled[j].isFocused=null;
			}
		}
		$scope.focusedBlock=null;
	}
	$scope.isBlockFocus=function(q, b){
		return $scope.focusedBlock.q === q && $scope.focusedBlock.b === b;
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
		$scope.unsetAllFocus();
		let title = $scope.document.data.annotations[$scope.title_index].reconciled[0].title;
		let json = JSON.stringify($scope.document.data);
		let status = $scope.document.status;
		$scope.saveInProgress = true;
		server.requestPhp({id: $stateParams["docId"], title, json, status}, 'save_doc').then(function (data) {
			$scope.saveInProgress = false;
			$scope.saveSuccessful = true;
			window.setTimeout($scope.continueToNextDoc, 1000);
		});
	}
	$scope.continueToNextDoc = function(){
		if($rootScope.latestQueryResults){
			const numOfResults = $rootScope.latestQueryResults.length;
			for(let i = 0; i < numOfResults - 1; i++){
				if($rootScope.latestQueryResults[i]["id"] === $scope.docId){
					$state.go('.', {
						docId : $rootScope.latestQueryResults[i + 1]["id"],
					});
					return;
				}
			}
		}
		$state.go('list', $rootScope.latestQuery);
	}
	$scope.continueToPrevDoc = function(){
		if($rootScope.latestQueryResults){
			const numOfResults = $rootScope.latestQueryResults.length;
			for(let i = 1; i < numOfResults; i++){
				if($rootScope.latestQueryResults[i]["id"] === $scope.docId){
					$state.go('.', {
						docId : $rootScope.latestQueryResults[i - 1]["id"],
					});
					return;
				}
			}
		}
		$state.go('list', $rootScope.latestQuery);
	}
	$scope.goToPage = function(pageNum){
		$scope.currPage = Math.min(Math.max(pageNum, 0), $scope.pages.length - 1)
	}
}]);