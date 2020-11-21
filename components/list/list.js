app.controller('list', ['$scope', '$stateParams', '$rootScope', '$state', 'server',
function($scope, $stateParams, $rootScope, $state, server){
	$scope.flags = ["implicit_date", "retired"];
	$scope.raised_flags = {};
	$scope.unraised_flags = {};
	$scope.docs = []
	$scope.getDocs = function(){
		let raised = [];
		let unraised = [];
		Object.keys($scope.raised_flags).forEach((f)=>{
			if($scope.raised_flags[f]){
				raised.push(f);
			}
		})
		Object.keys($scope.unraised_flags).forEach((f)=>{
			if($scope.unraised_flags[f]){
				unraised.push(f);
			}
		})
		let data = {raised:raised, unraised:unraised};
		server.requestPhp(data, 'list_docs').then(function (data) {
			$scope.docs = data;
		});
	}
	$scope.getDocs();
	$scope.goToPage = function(id){
		$state.transitionTo('singleDoc', { docId: id })
	}
}]);