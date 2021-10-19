USE inventory;
CREATE VIEW PublicGroceries AS (SELECT 
	Item.name AS Name, 
	Item.qty AS Quantity,  
	Item.units AS Units, 
	Location.name AS Location, 
	Item.expirationDate AS ExpirationDate 
FROM
	Item INNER JOIN 
	Location ON Item.location = Location.locationID INNER JOIN 
	Type ON Item.type = Type.typeID 
WHERE 
	Type.name LIKE 'Groceries' AND
	Item.public);
