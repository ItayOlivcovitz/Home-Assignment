-- Switch to the target database
USE mydb;

-- Show all tables in the database
SELECT 'Tables in mydb' AS ' ';
SHOW TABLES;

-- Display the counter value with custom text
SELECT CONCAT('Counter Value = ', count) AS ' ' FROM counter;

-- Display access log table content with headers
SELECT 'Access Log Table' AS ' ';
SELECT id AS 'ID', date AS 'Date', client_ip AS 'Client IP', server_ip AS 'Server IP'
FROM access_log;
