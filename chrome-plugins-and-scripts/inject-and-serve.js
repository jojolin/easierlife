var pingpong = (function () {
    'use strict'
    return function _pingpong() {

        var xhr = new XMLHttpRequest();

        xhr.open("GET", "http://your-own-serv-url"); ;

        xhr.onload = function () {
            // acquire the data
            var data = xhr.response;
            console.log(data);
            if (data == '') {
                console.log('no data available, loop');
            } else {
                /*
                TODO: add your own inject code here.
                handle your datalogic.
                 */
                var handledData = dataLogic(data);

                var xhr2 = new XMLHttpRequest();
                xhr2.open("POST", "http://your-own-serv-url");
                // send back handled data
                xhr2.send(handledData);
            }
            // keep going!
            _pingpong();

        };
        xhr.send();
    }
})();
pingpong();
