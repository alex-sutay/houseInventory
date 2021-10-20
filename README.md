# House Inventory
An inventory system for my house because I feel the need to over organize everything 

Essentially, I am setting up a database to hold household stock items, mostly groceries and leftovers, and then creating a web app and api to interact with and view the database, and finally a raspberry pi with a touchscreen, barcode scanner, and barcode printer so that you can easily tag and edit entries.

Currently, I just setup the database.

# Database Structure
Currently, the database has 7 tables and 4 views. Of the 7 tables, 3 are used for general data storage, 2 are used for lookups, and 2 are used for auth.
The 3 primary data tables are Item, Project, and ProjectResources.
Item is the table used to save inventory items, such as groceries, leftovers, or toiletries. 
Project is the table used for "projects", which are scheduled uses of the items. For example, if you plan to make waffles, but are worried the eggs will be used up, you can create a project titled waffles and allocate however many eggs you need, along with as many other items as you want.
ProjectResources is the table used to track what resources are claimed for specific projects. The Project table only saves the project title and date and the ProjectResources table saves what items and how many of each are used in the projects.
The 2 lookup tables are Type and Location, which are used to store the accepted values for item types and locations respectively.
Here are all of the relations:

Item(**itemID**, name, *type*, qty, units, *location*, expirationDate, public) <br>
&nbsp;&nbsp;&nbsp;&nbsp;Item(type) mei Type(typeID)  <br>
&nbsp;&nbsp;&nbsp;&nbsp;Item(location) mei Location(locationID) <br>
  
Project(**projectID**, name, expDate) <br>

ProjectResources(***project, item***, qty) <br>
&nbsp;&nbsp;&nbsp;&nbsp;ProjectResources(project) mei Project(projectID) <br>
&nbsp;&nbsp;&nbsp;&nbsp;ProjectResources(item) mei Item(itemID) <br>
  
Type(**typeID**, name) <br>

Location(**locationID**, name) <br>

Account(**userID**, userName, *type*, passHash) <br>
&nbsp;&nbsp;&nbsp;&nbsp;Account(type) mei AccountType(typeID) <br>
 
AccountType(**typeID**, name) <br>
