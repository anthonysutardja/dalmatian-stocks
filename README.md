# dalmatian-stocks

### Polymer
We've build a system composed of Polymer elements. A toolbar on the side houses a custom `<stock-list>` item which populates itself with `<stock-ticker>` elements that are an overlay on top of `<paper-button>`s. `<stock-card>` elements sit in the main body of the page, and they employ the use of `<paper-tabs>` and a custom `<stock-chart>` element. All these elements communicate with each other using `<core-signal>`s, and they access data using `<core-ajax>`s implented in `<stock-service>`s. 

Let's talk a little bit about each of these elements. 

#### Stock-Card
Stock-Card elements are composed of paper-tabs, and a stock-chart element. Events are passed into the card via core-signals, and data is pulled from our API through the stock-price-service element.

#### Stock-Chart
Stock-Chart is a Polymer implementation of Nvd3’s graph API. With a support for multiple date ranges, the stock-chart element handles data visualization through trend lines and colors corresponding to positive or negative growth.

#### Stock-List
Stock-List is a list of stock-ticker elements. Data is pulled from the API through the stock-service element, which is then used to populate the list.

#### Stock-Service
Stock-Service is an implementation of core-ajax that pulls data from the API. A list of stock symbols can be provided to get back a list of datapoint for those stocks.

#### Stock-Ticker
Stock-Ticker is an implementation of paper-buttons. It uses the Flexbox to beautifully layout the elements. 

### Data
Our application is built on top of Flask. We built a RESTful API that services the stock information for our front-end to visualize. This API pulls from both Yahoo finance and Google finance, but it cleans up the data nicely for easy access. 
tat
