(function(){function r(e,n,t){function o(i,f){if(!n[i]){if(!e[i]){var c="function"==typeof require&&require;if(!f&&c)return c(i,!0);if(u)return u(i,!0);var a=new Error("Cannot find module '"+i+"'");throw a.code="MODULE_NOT_FOUND",a}var p=n[i]={exports:{}};e[i][0].call(p.exports,function(r){var n=e[i][1][r];return o(n||r)},p,p.exports,r,e,n,t)}return n[i].exports}for(var u="function"==typeof require&&require,i=0;i<t.length;i++)o(t[i]);return o}return r})()({1:[function(require,module,exports){
var bs = require('binary-search');
var demoApp = 
angular.module('demoApp',[]);


demoApp.controller('SimpleController', function($scope)
	{
		

		$scope.order_book = []
		ws = new WebSocket("ws://localhost/websocket");
		ws.onopen = function(event)
		{
			ws.send('{"event":"subscribe", "pair": "BTCUSD"}');
		}
		ws.onmessage = function(event)
		{
			var data = JSON.parse(event.data);
			if (data.changes === undefined)
				return;
			data.changes.forEach(function(element)
			{
				pos = bs($scope.order_book, element, function(a,b){return a[1] - b[1];});
				console.log(pos);
				if (pos > 0)
				{
					if(element[0] == "BID")
						$scope.order_book[pos].bid_size = element[2];
					else
						$scope.order_book[pos].ask_size = element[2];

					if($scope.order_book[pos].bid_size == 0 && $scope.order_book[pos].ask_size == 0)
					{
						$scope.order_book.splice(pos,1);
					}
				}
				else
				{
					if(element[0] = "BID")
						$scope.order_book = $scope.order_book.slice(-pos).concat([{price:element[1], bid_size:element[2]}]).concat($scope.order_book.slice(-pos + 1 , ));
					else
						$scope.order_book = $scope.order_book.slice(-pos).concat([{price:element[1], ask_size:element[2]}]).concat($scope.order_book.slice(-pos + 1 , ));

				}

			});
			console.log($scope.order_book);
		};

	}


	);


},{"binary-search":2}],2:[function(require,module,exports){
module.exports = function(haystack, needle, comparator, low, high) {
  var mid, cmp;

  if(low === undefined)
    low = 0;

  else {
    low = low|0;
    if(low < 0 || low >= haystack.length)
      throw new RangeError("invalid lower bound");
  }

  if(high === undefined)
    high = haystack.length - 1;

  else {
    high = high|0;
    if(high < low || high >= haystack.length)
      throw new RangeError("invalid upper bound");
  }

  while(low <= high) {
    /* Note that "(low + high) >>> 1" may overflow, and results in a typecast
     * to double (which gives the wrong results). */
    mid = low + (high - low >> 1);
    cmp = +comparator(haystack[mid], needle, mid, haystack);

    /* Too low. */
    if(cmp < 0.0)
      low  = mid + 1;

    /* Too high. */
    else if(cmp > 0.0)
      high = mid - 1;

    /* Key found. */
    else
      return mid;
  }

  /* Key not found. */
  return ~low;
}

},{}]},{},[1]);
