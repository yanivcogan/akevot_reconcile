app.controller('list', ['$scope', '$stateParams', '$rootScope', '$state', 'server',
function($scope, $stateParams, $rootScope, $state, server){
	$scope.flags = ["retired", "suggested_title", "missing_title", "inconclusive_title", "implicit_date", "inconclusive_date", "standout_location", "missing_summary"];
	$scope.docStatusOptions = [
		{val:"PENDING", label:"חדש", selected: true},
		{val:"FINISHED", label:"הושלם", selected: false},
		{val:"INPROGRESS", label:"נותרה עבודה", selected: true}
	];
	$scope.raised_flags = {};
	$scope.unraised_flags = {};
	$scope.selected_filters = {};
	$scope.docs = [];
	$scope.flag_count = {};
	$scope.search = {term: ""};
	$scope.initializeSearch = function(){
		$scope.search.term = $stateParams.search?$stateParams.search:"";
		$scope.raised_flags = $stateParams.raised?JSON.parse($stateParams.raised):{};
		$scope.unraised_flags = $stateParams.unraised?JSON.parse($stateParams.unraised):{};
		const statuses = $stateParams.statuses?JSON.parse($stateParams.statuses):[];
		$scope.docStatusOptions.forEach(s=>{
			s.selected = statuses.indexOf(s.val) >= 0;
		})
		if(!statuses.length){
			$scope.docStatusOptions = [
				{val:"PENDING", label:"חדש", selected: true},
				{val:"FINISHED", label:"הושלם", selected: false},
				{val:"INPROGRESS", label:"נותרה עבודה", selected: true}
			];
		}
	};
	$scope.initializeSearch();
	$scope.getDocs = function(){
		let raised = [];
		let unraised = [];
		let statuses = [];
		let search = $scope.search.term;
		$scope.docStatusOptions.forEach(s=>{
			if(s.selected){
				statuses.push(s.val);
			}
		});
		Object.keys($scope.raised_flags).forEach((f)=>{
			if($scope.raised_flags[f]){
				raised.push(f);
			}
		});
		Object.keys($scope.unraised_flags).forEach((f)=>{
			if($scope.unraised_flags[f]){
				unraised.push(f);
			}
		});
		$state.go('.', {
			search : search,
			raised : JSON.stringify($scope.raised_flags),
			unraised : JSON.stringify($scope.unraised_flags),
			statuses : JSON.stringify(statuses)
		},
		{
			notify: false
		});
		let data = {raised, unraised, statuses, search};
		server.requestPhp(data, 'list_docs').then(function (data) {
			$scope.docs = data;
			$rootScope.latestQuery = {
				search : search,
				raised : JSON.stringify($scope.raised_flags),
				unraised : JSON.stringify($scope.unraised_flags),
				statuses : JSON.stringify(statuses)
			};
			$rootScope.latestQueryResults = $scope.docs;
		});
		server.requestPhp({}, 'flag_count').then(function (data) {
			//console.log(data);
			data.forEach(f=>{
				if(!$scope.flag_count[f.flag]) {
					$scope.flag_count[f.flag] = {};
				}
				$scope.flag_count[f.flag][f.status] = parseInt(f.count);
			});
			console.log($scope.flag_count)
		});
	};
	$scope.getFilteredFlagCount = (f) => {
		let count = 0;
		$scope.docStatusOptions.forEach(s=>{
			if(s.selected && $scope.flag_count[f] && $scope.flag_count[f][s.val])
				count += $scope.flag_count[f][s.val]
		});
		return count;
	};
	$scope.getDocs();
	$scope.goToPage = function(id){
		$state.transitionTo('singleDoc', { docId: id })
	}
	$scope.exportDocs = function(){
		server.requestPhp({}, 'export_docs').then(function (data) {
			let docs = data;
			docs = docs.map(d=>{
				let x = JSON.parse(d.json);
				let row = {};
				row.id = x.id;
				x.annotations.forEach(a=>{
					row[a.question] = a.reconciled.map(ans=>{
						let ansFields = Object.values(ans);
						let s = "";
						if(ansFields.length == 1){
							s = ansFields[0];
						}
						if(ansFields.length == 2){
							s = ansFields[1] + "|" + ansFields[0];
						}
						if(ansFields.length == 4){
							s = ansFields[1] + "|" + ansFields[0] + "%" + ansFields[2] + "|" + ansFields[3];
						}
						return JSON.stringify(s.replaceAll(",", "COMMA"));
					}).join("#");
				})
				return Object.values(row).join("^")
			})
			let csvContent = docs.join("\n");
			let blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
			if (navigator.msSaveBlob) { // IE 10+
				navigator.msSaveBlob(blob, filename);
			} else {
				let link = document.createElement("a");
				if (link.download !== undefined) { // feature detection
					// Browsers that support HTML5 download attribute
					var url = URL.createObjectURL(blob);
					link.setAttribute("href", url);
					link.setAttribute("download", "export_reconciled.csv");
					link.style.visibility = 'hidden';
					document.body.appendChild(link);
					link.click();
					document.body.removeChild(link);
				}
			}
		});
	}
}]);