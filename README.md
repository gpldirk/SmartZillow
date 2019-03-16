# SmartZillow


•	Designed a real estate search and value prediction system using Service-Oriented Architecture (SOA).

•	Built the frontend server with Node.js, Express, Bootstrap and Bing Map API.

•	Implemented a distributed real estate web scraping system to collect real-time property information using MongoDB and               RabbitMQ.

•	Designed and developed a real estate value online prediction system with TensorFlow and Linear Regression.


1. SmartZillow is a real estate search and property value estimation system. The system collects property information available on Zillow.com, and provides a value estimation for a specific property. The system consists of four major parts: a Node.js web server, a backend server, a data fetching system and a machine learning system. The web server is for property search and rendering details. The backend server is serving all property content requested by web server through RPC. Data fetching system is used for collecting and processing property data asynchronously. The machine learning system is using linear regression to train and serve a model for property value estimation.

2. The entire system was designed using Service Oriented Architecture by decoupling all subsystems. Each subsystem of the architecture is independent and isolated, which can be tested and improved individually. In the project, web server handles web rendering work only, which is built with Node.js and Express. Web server requests backend server for content through RPC. The backend server is responsible for all business logic work including property search in MongoDB and getting value estimation from Machine Learning serving system. In order to collect property information, a data fetching system using web scraping and Zillow public API based on RabbitMQ is implemented. At last, some typical features are selected to train a property value model with TensorFlow and deploy a machine learning serving system. 


![project architecture overview](https://github.com/gpldirk/SmartZillow/blob/master/project%20modules.png)


### Links of the project

The webpage address: 

The youtube demo address: 
