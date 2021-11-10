USE inventory;

DROP VIEW IF EXISTS EasyMeals;

CREATE VIEW EasyMeals AS (SELECT 
	Item.name AS Name, 
	Type.name AS Type,
	TRIM(Item.qty)+0 AS Quantity,  
	Item.units AS Units, 
	Location.name AS Location, 
	Item.expirationDate AS ExpirationDate
FROM
	Item INNER JOIN 
	Location ON Item.location = Location.locationID LEFT JOIN (
	       SELECT ProjectResources.item, SUM(ProjectResources.qty) AS total 
		FROM ProjectResources
		GROUP BY item) 	
	Resources ON Item.itemID = Resources.item INNER JOIN 
	Type ON Item.type = Type.typeID 
WHERE 
	Type.name LIKE 'Leftovers' OR
	Type.name LIKE 'Easy Meal');
