Item Catalog Application

What is it?
———————————
The Item Catalog application is the third project in the Full Stack Web Developer Nanodegree. The application is designed to provide a list of items within a variety of categories. Users have the ability to post, edit, and delete their own categories and items.


The Latest Version
——————————————————
The latest version of the application can be found at https://github.com/slikqaz/fullstack/tree/master/vagrant/catalog.


Configuration Instructions
——————————————————————————
The external libraries and environments used are:

	Flask (http://flask.pocoo.org/)
	SQLAlchemy (http://www.sqlalchemy.org/)
	Oauth2client.client (http://oauth.net/2/)
	Vagrant (https://www.vagrantup.com/)

The internal libraries used are: httplib2, json, requests, random, string, os, and sys.


Installation and Run Instructions
—————————————————————————————————
For installation and run, use the following:

	1. Open the terminal.
	2. Change the current directory to the vagrant folder.
	3. Type ‘vagrant up’.
	4. Type ‘vagrant ssh’.
	5. Change the current directory to the catalog folder.
	6. If you would like to start a new database, delete the catalog.db and type ‘python database_setup.py’.
	7. Type ‘project.py’.
	8. Open the browser and type ‘http://localhost:8080/catalog'.
	9. Sign in using Google + to add, delete, and edit your own entries.


Operating Instructions
——————————————————————
Available public websites:

	Home Page: http://localhost:8080/catalog
	Log In: http://localhost:8080/login
	Category And Items In Category: http://localhost:8080/catalog/<int:category_id>/<category_name>/items
	Item: http://localhost:8080/catalog/<int:category_id>/<category_name>/<int:item_id>/<item_name>

Available JSON public endpoints:

	Category List JSON: http://localhost:8080/catalog/json
	Items In Category List JSON: JSONhttp://localhost:8080/catalog/<int:category_id>/<category_name>/json
	Item JSON: http://localhost:8080/catalog/<int:category_id>/<category_name>/<int:item_id>/<item_name>/json