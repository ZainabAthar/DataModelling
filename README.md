# Data Modelling
SQL Server to Cube.js Conversion Script
This script connects to a SQL Server database, retrieves information about the tables, and generates JavaScript files for Cube.js integration. Each .js file represents a Cube.js cube corresponding to a table in the SQL Server database.

Prerequisites
Python 3.x
pyodbc library installed
SQL Server ODBC Driver 18 installed
Setup
Install Python Dependencies:

Ensure you have pyodbc installed. If not, you can install it using pip:

bash
Copy code
pip install pyodbc
SQL Server ODBC Driver:

Ensure that you have the ODBC Driver 18 for SQL Server installed. You can download it from the official Microsoft website.

Database Credentials:

Update the connection parameters in the script with your SQL Server database details:

python
Copy code
server = '***.***.***.**'
database = '********'
username = '********'
password = '*************'
Script Overview
The script performs the following tasks:

Connect to the Database:

Establishes a connection to the SQL Server database using the provided credentials.
Retrieves the list of tables in the database.
Generate Cube.js Files:

For each table, a .js file is generated containing:
Cube name and SQL table reference.
Joins (with unique names) based on foreign key relationships.
Dimensions (with unique names) based on the columns in the table.
Measures, including a count measure and sum/average measures for numeric columns.
Placeholder for pre-aggregations.
Output:

The generated .js files are saved in the js_files directory.
Running the Script
Update the Script:

Make sure all the connection parameters and other configurations are correctly set.

Run the Script:

Execute the script in your Python environment:

bash
Copy code
python your_script_name.py
Check the Output:

After running the script, check the js_files directory for the generated Cube.js files.

Customization
Joins: The script filters and ensures unique joins based on foreign key relationships.
Dimensions: Handles different data types (number, time, string) and ensures unique property names.
Measures: Includes default count measures and sum/average measures for numeric columns.
Pre-Aggregations: Add your pre-aggregation logic in the generated files.
Troubleshooting
Ensure your SQL Server is accessible and the credentials are correct.
If the ODBC connection fails, verify that the ODBC Driver 18 is installed and correctly referenced in the connection string.
