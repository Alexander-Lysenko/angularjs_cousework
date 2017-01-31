var app = angular.module('AnimeApp', [
    'ngRoute',
    'ngCookies']);
app.config(['$locationProvider', function ($locationProvider) {
    $locationProvider.hashPrefix('');
}]);
app.config(function ($routeProvider) {
    $routeProvider
        .when("/", {
            templateUrl: "/static/edit.html",
            controller: "AnimeListController"
        })
        .when("/login", {
            templateUrl: "/static/login.html",
            controller: "LoginController"
        })
        .when("/signup", {
            templateUrl: "/static/signup.html",
            controller: "SignupController"
        })
        .when("/profile", {
            templateUrl: "/static/profile.html",
            controller: "ProfileController"
        })
        .otherwise({redirectTo: '/login'});
});

app.controller('SignupController', function ($scope, $http) {
    $scope.submitForm = function (user, userForm) {
        if (userForm.$valid) {
            $http.post("/api/signup", user).then(function (response) {
                if (response.data == 'OK') {
                    $scope.message = 'Вы успешно зарегистрировались. Теперь вы можете зайти под своим никнеймом.';
                    $scope.error = null;
                }
                else {
                    $scope.error = 'Ошибка. Этот никнейм уже занят';
                    $scope.message = null;
                    console.log(response);
                }
            })
        }
    };

    $scope.verifyName = function (username) {
        $http.post("/api/login/verify/" + username).then(function (request) {
            if (request.data == 'OK') {
                $scope.status = 'Этот никнейм уже занят';
            }
            else {
                $scope.status = 'Этот никнейм свободен';
            }
        });
    };
});
app.controller('LoginController', ['$scope', '$rootScope', '$location', 'AuthenticationService',
    function ($scope, $rootScope, $location, AuthenticationService) {

        $scope.login = function () {
            $scope.dataLoading = true;
            AuthenticationService.Login($scope.username, $scope.password, function (response) {
                if (response.data != 'Fail') {
                    AuthenticationService.SetCredentials($scope.username, $scope.password);
                    $location.path('/');
                } else {
                    $scope.error = response.message;
                    $scope.dataLoading = false;
                }
            });
        };
        $scope.logout = function () {
            // reset login status
            if (confirm('Вы действительно желаете выйти из своего аккаунта?')) {
                AuthenticationService.ClearCredentials();
                $location.path('/login');
                console.log('Successful logout');
            }
        }
    }]);
app.controller('AnimeListController', function ($scope, $http) {
    $scope.requestData = function () {
        $http.get('/api/anime/list').then(function (request) {
            $scope.anime_list = request.data.anime_list;
            $scope.username = request.data.user_name;
        });
    };

    $scope.submitForm = function (edit, editForm) {
        if (editForm.$valid) {
            $http.post("/api/anime/add", edit).then(function (request) {
                if (request.data == 'OK') {
                    $scope.message = 'Запись успешно добавлена';
                    $scope.error = null;
                    console.log('Добавлена запись: ' + edit.title);
                    $scope.edit = null;
                }
                else {
                    $scope.error = 'Ошибка: Аниме c таким именем уже есть в коллекции';
                    $scope.message = null;
                    console.log('Ошибка');
                }
            }).then(this.requestData())
        }
    };

    $scope.removeAnime = function (number) {
        if (confirm('Вы действительно желаете удалить это аниме из коллекции?')) {
            $http.post('/api/anime/rm/' + number).then(this.requestData());
            console.log(' Deletion successful. id = ' + number);
        }
        else {
            console.log('Deletion cancelled');
        }
    };
});
app.controller('ProfileController', ['$scope', function ($scope) {
    $scope.pushData = function () {

    }
}]);

app.run(['$rootScope', '$location', '$cookieStore', '$http',
    function ($rootScope, $location, $cookieStore, $http) {
        // keep user logged in after page refresh
        $rootScope.globals = $cookieStore.get('globals') || {};
        if ($rootScope.globals.currentUser) {
            $http.defaults.headers.common['Authorization'] = 'Basic ' + $rootScope.globals.currentUser.authdata;
            // jshint ignore:line
        }

        $rootScope.$on('$locationChangeStart', function (event, next, current) {
            // redirect to login page if not logged in
            /*var restrictedPage = $.inArray($location.path(), ['/', '/profile']) === -1;
             var loggedIn = $rootScope.globals.currentUser;
             if (restrictedPage && !loggedIn) {
             $location.path('/login');
             }*/
            if (($location.path() !== '/login' && $location.path() !== '/signup') && !$rootScope.globals.currentUser) {
                $location.path('/login');
            }
        });
    }]);
