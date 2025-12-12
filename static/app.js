var username = null;
var password = null;
var date = null;
var movieID = null;
var type = null;
var seatNo = null;
var seatClass = null;
var movieTime = null;
var showID = null;
var startShowing = null;
var endShowing = null;
var showTime = null;
var showDate = null;
var priceID = null;

function login(){
	if(username === null){
		username = $("[name='username']")[0].value;
		password = $("[name='password']")[0].value;
	}
	var form = {
		'username' : username,
		'password' : password
	};
	$.ajax({
		type: 'POST',
		url: '/login',
		data: form,
		success: function(response){
			$('.module').html(response);
			$('.module').addClass('module-after-login');
			$('.login-header').addClass('after-login');
			$('#datepicker-cashier').pickadate({
				min : new Date(),
				formatSubmit: 'yyyy-mm-dd', 
 				hiddenName: true,
 				placeholder: '选择日期',
 				onSet: function( event ) {
 					if ( event.select ) {
 						$('#datepicker-cashier').prop('disabled', true);
 						getMoviesShowingOnDate(this.get('select', 'yyyy-mm-dd' ));
 					}
 				}
			});
		}
	});
}

// Functions for cashier
function getMoviesShowingOnDate(mdate){
	date = mdate;
	$.ajax({
		type: 'POST',
		url: '/getMoviesShowingOnDate',
		data: {'date' : date},
		success: function(response){
			$('#movies-on-date').html(response);
		}
	});
}
function selectMovie(movID, mtype){
	movieID = movID;
	type = mtype;
	$.ajax({
		type: 'POST',
		url: '/getTimings',
		data: {
			'date' : date,
			'movieID': movieID,
			'type' : type
		},
		success: function(response){
			$('#movies-on-date button').prop('disabled', true);
			$('#timings-for-movie').html(response);
		}
	});
}
function selectTiming(mshowID){
    showID = mshowID;
    

    $('#timings-for-movie button').prop('disabled', true);
    

    getSeats();
}
function getSeats(){
	$.ajax({
		type: 'POST',
		url: '/getAvailableSeats',
		data: {'showID' : showID},
		success: function(response){
			$('#available-seats').html(response);
		}
	});
}
function selectSeat(no, sclass){
	seatNo = no;
	seatClass = sclass;
	$.ajax({
		type: 'POST',
		url: '/getPrice',
		data: {
			'showID' : showID,
			'seatClass' : seatClass
			},
		success: function(response){
			$('#price-and-confirm').html(response);
		}
	});
}
function confirmBooking(){
	$.ajax({
		type: 'POST',
		url: '/insertBooking',
		data: {
			'showID' : showID,
			'seatNo' : seatNo,
			'seatClass' : seatClass
			},
		success: function(response){
			$('#available-seats button').prop('disabled', true);
			$('#price-and-confirm').html(response);
		}
	});
}

// Functions for manager
function viewBookedTickets(){
	$('#options button').prop('disabled', true);
	$('#manager-dynamic-1').html('<input id="datepicker-manager-1" placeholder="选择查看日期">');
	$('#datepicker-manager-1').pickadate({
				formatSubmit: 'yyyy-mm-dd', 
 				hiddenName: true,
 				onSet: function( event ) {
 					if ( event.select ) {
 						$('#datepicker-manager-1').prop('disabled', true);
 						getShowsShowingOnDate(this.get('select', 'yyyy-mm-dd' ));
 					}
 				}
	});
}
function getShowsShowingOnDate(mdate){
	date = mdate;
	$.ajax({
		type: 'POST',
		url: '/getShowsShowingOnDate',
		data: {'date' : date},
		success: function(response){
			$('#manager-dynamic-2').html(response);
		}
	});
}
function selectShow(mshowID){
	showID = mshowID;
	$.ajax({
		type: 'POST',
		url: '/getBookedWithShowID',
		data: {'showID' : showID},
		success: function(response){
			$('#manager-dynamic-2 button').prop('disabled', true)
			$('#manager-dynamic-3').html(response);
		}
	});
}
function insertMovie(){
	$('#options button').prop('disabled', true);
	$.ajax({
		type: 'GET',
		url: '/fetchMovieInsertForm',
		success: function(response){
			$('#manager-dynamic-1').html(response);
			$('#datepicker-manager-2').pickadate({
				formatSubmit: 'yyyy-mm-dd', 
 				hiddenName: true,
 				onSet: function( event ) {
 					if ( event.select ) {
 						startShowing = this.get('select', 'yyyy-mm-dd' );
 					}
 				}
			});
			$('#datepicker-manager-3').pickadate({
				formatSubmit: 'yyyy-mm-dd', 
 				hiddenName: true,
 				onSet: function( event ) {
 					if ( event.select ) {
 						endShowing = this.get('select', 'yyyy-mm-dd' );
 					}
 				}
			});
		}
	});
}
function filledMovieForm(){
	availTypes = $('[name="movieTypes"]')[0].value.trim();
	movieName = $('[name="movieName"]')[0].value;
	movieLang = $('[name="movieLang"]')[0].value;
	movieLen = $('[name="movieLen"]')[0].value;
	
	if($('#datepicker-manager-2')[0].value == '' || $('#datepicker-manager-3')[0].value == '' ||
	movieName == '' || movieLang == '' || movieLen == '' || availTypes == '')
		$('#manager-dynamic-2').html('<h5>请填写所有信息</h5>');
	else if(! $.isNumeric(movieLen))
		$('#manager-dynamic-2').html('<h5>电影时长必须为数字（分钟）</h5>');
	else if(Date.parse(startShowing) > Date.parse(endShowing))
		$('#manager-dynamic-2').html("<h5>首映日期必须早于下映日期</h5>");
	else{
		movieLen = parseInt(movieLen, 10);
		$.ajax({
			type: 'POST',
			url: '/insertMovie',
			data: {
				'movieName' : movieName,
				'movieLen' : movieLen,
				'movieLang' : movieLang,
				'types' : availTypes,
				'startShowing' : startShowing,
				'endShowing' : endShowing
			},
			success: function(response){
				$('#manager-dynamic-2').html(response);
			}
		});
	}
}
function createShow(){
	$('#options button').prop('disabled', true);
	$('#manager-dynamic-1').html('<input id="datepicker-manager-3" placeholder="选择排片日期"><input id="timepicker-manager-1" placeholder="选择开场时间"><button onclick="getValidMovies()">查询</button>');
	$('#datepicker-manager-3').pickadate({
				formatSubmit: 'yyyy-mm-dd', 
 				hiddenName: true,
 				min: new Date(),
 				onSet: function( event ) {
 					if ( event.select ) {
 						showDate = this.get('select', 'yyyy-mm-dd' );
 					}
 				}
	});
	$('#timepicker-manager-1').pickatime({
				formatSubmit: 'HHi',
 				hiddenName: true,
 				interval: 15,
 				min: new Date(2000,1,1,8),
  				max: new Date(2000,1,1,22),
 				onSet: function( event ) {
 					if ( event.select ) {
 						showTime = parseInt(this.get('select', 'HHi' ), 10);
 					}
 				}
	});
}
function getValidMovies(){
	if($('#timepicker-manager-1')[0].value == '' || $('#datepicker-manager-3')[0].value == ''){
		$('#manager-dynamic-2').html('<h5>请选择日期和时间</h5>');
		return;
	}
	$('#manager-dynamic-1 input,#manager-dynamic-1 button').prop('disabled', true)
	$.ajax({
			type: 'POST',
			url: '/getValidMovies',
			data: {
				'showDate' : showDate
			},
			success: function(response){
				$('#manager-dynamic-2').html(response);
			}
		});
}
function selectShowMovie(movID,types){
	movieID = movID;
	$('#manager-dynamic-2 button').prop('disabled', true);
	$('#manager-dynamic-3').html('<h4>选择放映制式</h4>');
	
	var projectionTypes = ['2D', '3D', '4DX'];
	projectionTypes.forEach(function(t){
		$('#manager-dynamic-3').append('<button onclick="selectShowType('+("'"+t+"'")+')">'+t+'</button>');
	});
}
function selectShowType(t){
	type = t;
	$.ajax({
			type: 'POST',
			url: '/getHallsAvailable',
			data: {
				'showDate' : showDate,
				'showTime' : showTime,
				'movieID' : movieID
			},
			success: function(response){
				$('#manager-dynamic-3 button').prop('disabled', true);
				$('#manager-dynamic-4').html(response);
			}
		});
}
function selectShowHall(hall){
	$.ajax({
			type: 'POST',
			url: '/insertShow',
			data: {
				'hallID' : hall,
				'movieType' : type,
				'showDate' : showDate,
				'showTime' : showTime,
				'movieID' : movieID
			},
			success: function(response){
				$('#manager-dynamic-4 button').prop('disabled', true);
				$('#manager-dynamic-5').html(response);
			}
		});
}
function alterPricing(){
	$('#options button').prop('disabled', true);
	$.ajax({
			type: 'GET',
			url: '/getPriceList',
			success: function(response){
				$('#manager-dynamic-1').html(response);
			}
		});
}
function alterPrice(mpriceID){
	priceID = mpriceID;
	$('#manager-dynamic-1 button').prop('disabled', true);
	$('#manager-dynamic-2').html('<input type="number" name="new_price" placeholder="输入新价格 (¥)"><button onclick="changePrice()">修改</button>');
}
function changePrice(){
	newPrice = $('#manager-dynamic-2 input')[0].value;
	$.ajax({
			type: 'POST',
			url: '/setNewPrice',
			data: {
				'priceID' : priceID,
				'newPrice' : newPrice
			},
			success: function(response){
				$('#manager-dynamic-3').html(response);
			}
		});
}