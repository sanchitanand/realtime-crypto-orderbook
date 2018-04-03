
var express = require('express');
var app = express();
const cors = require('cors');

var corsOptions = {
	origin:'*',
	optionsSuccessStatus:200
};

app.use(cors(corsOptions));
app.use(express.static(__dirname + '/assets'));
app.get('/',function(req,res){
	res.sendFile(__dirname + '/index.html');
})

app.listen(80,function(){
	console.log('app listening on port 80')
});
