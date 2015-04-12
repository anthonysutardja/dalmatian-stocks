
    var stockCard;

    function getStockCard() {
      stockCard = document.getElementsByTagName('stock-card')[0];
    };

    function callback_function(object) {
      return object;
    };

    var xhr = new XMLHttpRequest();
    xhr.open("GET", "/api/stocks.json", true);
    xhr.onreadystatechange = function() {
        if (xhr.readyState == 4) {
            callback_function(JSON.parse(xhr.responseText));
        };
    };
    xhr.send();

    function reload(stock) {
      var index = stock.childNodes[1].firstChild.data;
      var stockJSON = JSON.parse(callback_function(xhr.responseText))[index];
      console.log(stockJSON.name);

      var h2 = stockCard.childNodes[1];
      h2.innerHTML = stockJSON.name;
    };