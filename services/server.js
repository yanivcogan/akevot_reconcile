app.factory('server', ['$rootScope', '$http', '$q', '$state', '$timeout', function ($rootScope, $http, $q, $state, $timeout) {
var timeoutMillis = 5000;
	return {
		requestPhp: function (data, type) {
			var deferred = $q.defer();
			var httpDetails = {
				url: "./server/datagate.php?type=" + type,
				method: "POST",
				data: angular.toJson(data),
				contentType: "application/json",
				timeout:timeoutMillis,
				config:{timeout:timeoutMillis}
			};

			if (!data.req) {
				httpDetails.transformRequest = angular.identity;
				httpDetails.headers = { 'Content-Type': undefined};
				httpDetails.contentType = undefined;
			}
			$http(httpDetails).then(function (json) {
				deferred.resolve(json.data);
			})
			return deferred.promise;
		}
}}]);