USE inventory;

DROP VIEW IF EXISTS PublicGroceries;

CREATE VIEW PublicGroceries AS (SELECT 
	Item.name AS Name, 
	TRIM(Item.qty)+0 AS Quantity,  
	Item.units AS Units, 
	Location.name AS Location, 
	Item.expirationDate AS ExpirationDate 
FROM
	Item INNER JOIN 
	Location ON Item.location = Location.locationID INNER JOIN 
	Type ON Item.type = Type.typeID 
WHERE 
	Item.public);
