USE inventory;

DROP VIEW IF EXISTS ActiveProjects;

CREATE VIEW ActiveProjects AS (SELECT 
	Project.projectID AS ID,
	Project.name AS Name, 
	Project.expDate AS ExpectedDate,
	Resources.needed AS ResourcesNeeded
FROM
	Project LEFT JOIN (
	       SELECT ProjectResources.project, GROUP_CONCAT(Item.name, ': ', ProjectResources.qty, ' ', Item.units) AS needed
		FROM ProjectResources INNER JOIN 
		Item ON Item.itemID = ProjectResources.item
		GROUP BY project) 	
	Resources ON Project.projectID = Resources.project
WHERE
	Project.inactive = 0);
