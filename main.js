const app = angular.module('reconciler', ['ui.router']);
app.config(function ($stateProvider, $urlRouterProvider, $compileProvider) {
	$urlRouterProvider.otherwise("/list");
	$stateProvider
	.state('singleDoc', {
		url: '/doc/:docId',
		views: {
			"main": {
				controller: 'singleDoc',
				templateUrl: './components/singleDoc/singleDoc.html'
			}
		}
	})
	.state('list', {
		url: '/list?:search&:raised&:unraised&:statuses',
		views: {
			"main": {
				controller: 'list',
				templateUrl: './components/list/list.html'
			}
		},
		reloadOnSearch: false
	})
});