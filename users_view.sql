USE inventory;

DROP VIEW IF EXISTS Users;

CREATE VIEW Users AS (SELECT
       	Account.userID AS ID,
       	Account.userID,
       	Account.userName,
	AccountType.name AS type,
       	Account.passHash
FROM 
	Account INNER JOIN 
	AccountType ON Account.type = AccountType.typeID);
