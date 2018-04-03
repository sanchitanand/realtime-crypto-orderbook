var demoApp = 
angular.module('demoApp',[]);

var MY_WEBSOCKET = "your endpoint here";

demoApp.factory('websocketService', function () {
        return {
            start: function (url, pair, callback) {
                var websocket = new WebSocket(url);
                websocket.onopen = function () {
                	websocket.send('{"event":"subscribe", "pair":"'+pair+'"}');
                };
                websocket.onclose = function () {
                };
                websocket.onmessage = function (evt) {
                    callback(evt);
                };
                return websocket;
            }
        }
    }
);

function inOrder(arr, item, reverse) {
				    /* Insert item into arr keeping low to high order. Use reverse to reverse it */
				    let ix = 0;
				    if(!reverse)
				    {
					    while (ix < arr.length) {
					        //console.log('ix',ix);
					        if (item[1] <= arr[ix].price) { break; }
					        ix++;
					    }
					    if (arr.length > 0 && ix < arr.length && arr[ix].price == item[1])
					   	{
					   		arr[ix].size = item[2];
					   		//console.log(arr);
					   	}
					   	else
					   	{
						    arr.splice(ix,0,{price:item[1],size:item[2]});
						    //console.log(arr);
						}
					}
					else
					{	
						while (ix < arr.length) {
					        //console.log('ix',ix);
					        if (item[1] >= arr[ix].price) { break; }
					        ix++;
					    }
					    if (arr.length > 0 && ix < arr.length && arr[ix].price == item[1])
					   	{
					   		arr[ix].size = item[2];
					   		//console.log(arr);
					   	}
					   	else
					   	{
						    arr.splice(ix,0,{price:item[1],size:item[2]});
						    //console.log(arr);
						}

					}
				}



demoApp.controller('SimpleController', function($scope,websocketService)
	{


		$scope.bidLimit = 50;
		$scope.askLimit=50;
		$scope.size = [10,20,50,100,200,500,1000,5000];
		$scope.pairs = ["BTCUSD","ETHUSD","LTCUSD","LTCBTC","ETHBTC"];
		$scope.pair = "BTCUSD";
		$scope.ws = undefined;
		$scope.$watch("pair",
			function()
			{
				$scope.bids = [];
				$scope.asks = [];
				if ($scope.ws)
					$scope.ws.close();
				$scope.ws = websocketService.start(MY_WEBSOCKET,$scope.pair, function(evt)
					{
						var data = JSON.parse(evt.data);
						if(!data.changes)
							return;
						console.log(data.changes.length);
						$scope.$apply(function(){
							
							let i;
							for(i=0;i<data.changes.length;i++)
							{
								if (data.changes[i][0] == "ASK")
									inOrder($scope.asks, data.changes[i] , false);
								else
									inOrder($scope.bids, data.changes[i] , true);
							}
							
							$scope.asks = $scope.asks.filter(x=>x.size > parseFloat(0));
							$scope.bids = $scope.bids.filter(x=>x.size > parseFloat(0));


							});

							

					});

			});
	});
		
				


		

