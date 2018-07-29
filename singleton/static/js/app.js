angular.module('singleton', ['singletonControllers'])

// Change brackets used in templates from {{ }} to {[ ]}
// as jinja2 uses {{ }}
.config(['$interpolateProvider', function ($interpolateProvider) {
    $interpolateProvider.startSymbol('{[');
    $interpolateProvider.endSymbol(']}');
}]);

