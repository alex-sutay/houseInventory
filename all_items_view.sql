USE inventory;
DROP VIEW IF EXISTS AllItems;
CREATE VIEW AllItems AS (SELECT 
	Item.itemID AS ID,
	Item.name AS Name, 
	Type.name AS Type,
	TRIM(Item.qty)+0 AS Quantity,  
	TRIM(IF(Resources.total IS NULL, Item.qty, (Item.qty - Resources.total)))+0 AS QuantityUnallocated,
	Item.units AS Units, 
	Location.name AS Location, 
	Item.expirationDate AS ExpirationDate, 
	IF(Item.public, 'Yes', 'No') AS Public
FROM
	Item INNER JOIN 
	Location ON Item.location = Location.locationID LEFT JOIN (
	       SELECT ProjectResources.item, SUM(ProjectResources.qty) AS total 
		FROM ProjectResources
		GROUP BY item) 	
	Resources ON Item.itemID = Resources.item INNER JOIN 
	Type ON Item.type = Type.typeID); 
