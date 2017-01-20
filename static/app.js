var app = angular.module('AnimeApp', ["ngRoute"])
    .config( ['$routeProvider', function($routeProvider) {
    $routeProvider
    .when('/login', {
    templateUrl: '/templates/login.html',
        controller: 'Login'
    })
    .when('/signup', {
    templateUrl: '/templates/signup.html',
        controller: 'Signup'
    });
}]);

app.controller('HomepageController', ['$scope', function ($scope) {
    $scope.message = "Hello, World!";
    //Проверка сессии
}]);

app.controller('SignupController', ['$scope', function ($scope, $http) {
    $scope.response = {};
    $scope.submitForm = function (user, userForm) {
        // check to make sure the form is completely valid
        if (userForm.$valid) {
            /*$http.post("/signup", user).success(function (answer) {
                $scope.response = answer;
            });*/
            alert(angular.toJson(user))
        }//не работает POST запрос
    };
}]);

app.controller('LoginController', function ($scope){//, $rootScope, AUTH_EVENTS, AuthService) {
    $scope.submitForm = function (auth, loginForm) {
         /*AuthService.login(loginForm).then(function () {
         $rootScope.$broadcast(AUTH_EVENTS.loginSuccess);
         }, function () {
         $rootScope.$broadcast(AUTH_EVENTS.loginFailed);
         });*/
         alert(angular.toJson(auth))
    };
});

app.controller('AnimeAddController', function ($scope, $http){
    $scope.response = {};
    $scope.submitForm = function (edit, editForm) {
        if (editForm.$valid) {
            alert(angular.toJson(edit))
            $http.post("/api/anime/add", edit).success(function (answer) {
                $scope.response = answer;
            });
        };
    };
});

app.controller('AnimeListController', function ($scope, $http){
    $http.get('/static/countries.json').success(function(data) {
        $scope.request = data;
    });
});