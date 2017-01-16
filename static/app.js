var app = angular.module('AnimeApp', [])
app.controller('Homepage', ['$scope', function ($scope) {
    $scope.message = "Hello, World!";
}]);
app.controller('Signup', ['$scope', function ($scope, $http) {
    $scope.response = {};
    $scope.submitForm = function (user, userForm) {
        // check to make sure the form is completely valid
        if (userForm.$valid) {
            /*$http.post("/signup", userForm).success(function (answer) {
                $scope.response = answer;
            });*/
            alert(angular.toJson(user))
        }
    };
}]);

app.controller('Login', function ($scope){//, $rootScope, AUTH_EVENTS, AuthService) {
    $scope.submitForm = function (auth, loginForm) {
         /*AuthService.login(loginForm).then(function () {
         $rootScope.$broadcast(AUTH_EVENTS.loginSuccess);
         }, function () {
         $rootScope.$broadcast(AUTH_EVENTS.loginFailed);
         });*/
         alert(angular.toJson(auth))
    };
})
