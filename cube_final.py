import pyodbc
import os

# Define connection parameters
server = '***.***.***.**'
database = '********'
username = '********'
password = '*************'

# Create a connection string
conn_str = (
    r'DRIVER={ODBC Driver 18 for SQL Server};'
    f'SERVER={server};'
    f'DATABASE={database};'
    f'UID={username};'
    f'PWD={password};'
    f'TrustServerCertificate=yes'
)

conn = pyodbc.connect(conn_str)
cursor = conn.cursor()

# Fetch tables
cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'")
tables = [row.TABLE_NAME for row in cursor.fetchall()]

output_dir = 'js_files'
os.makedirs(output_dir, exist_ok=True)

def make_unique_name(existing_names, name):
    """Ensure the property name is unique by appending a number if necessary."""
    original_name = name
    i = 1
    while name in existing_names:
        name = f"{original_name}_{i}"
        i += 1
    existing_names.add(name)
    return name

for table in tables:
    js_data = []
    
    # Set to track used property names
    used_names = set()

    # Table name for cube
    js_data.append(f"cube(`{table}`, {{")
    js_data.append(f"  sql_table: `dbo.{table}`,")
    js_data.append(f"  data_source: `default`,")
    
    # Joins
    cursor.execute(f"""
    SELECT 
        tp.name AS PARENT_TABLE,
        cp.name AS PARENT_COLUMN,
        ref.name AS REFERENCED_TABLE,
        cref.name AS REFERENCED_COLUMN
    FROM
        sys.foreign_keys AS fk
        INNER JOIN sys.tables AS tp ON fk.parent_object_id = tp.object_id
        INNER JOIN sys.columns AS cp ON fk.parent_object_id = cp.object_id AND cp.column_id IN (
            SELECT parent_column_id 
            FROM sys.foreign_key_columns AS fkc 
            WHERE fkc.constraint_object_id = fk.object_id
        )
        INNER JOIN sys.tables AS ref ON fk.referenced_object_id = ref.object_id
        INNER JOIN sys.columns AS cref ON fk.referenced_object_id = cref.object_id AND cref.column_id IN (
            SELECT referenced_column_id 
            FROM sys.foreign_key_columns AS fkc 
            WHERE fkc.constraint_object_id = fk.object_id
        )
    WHERE
        tp.name = '{table}'
    """)
    joins = cursor.fetchall()

    # Filter unique joins by considering only distinct REFERENCED_TABLE and REFERENCED_COLUMN
    unique_joins = []
    seen_joins = set()
    for join in joins:
        join_key = (join.REFERENCED_TABLE, join.REFERENCED_COLUMN)
        if join_key not in seen_joins:
            seen_joins.add(join_key)
            unique_joins.append(join)
    
    if unique_joins:
        js_data.append(f"  joins: {{")
        for join in unique_joins:
            join_name = make_unique_name(used_names, join.REFERENCED_TABLE.lower())
            js_data.append(f"    {join_name}: {{")
            js_data.append(f"      sql: `${{CUBE}}.{join.PARENT_COLUMN} = ${{{join.REFERENCED_TABLE.lower()}}}.{join.REFERENCED_COLUMN}`,")
            js_data.append(f"      relationship: `many_to_one`")
            js_data.append(f"    }},")
        js_data.append(f"  }},")

    # Dimensions
    cursor.execute(f"""
    SELECT COLUMN_NAME, DATA_TYPE
    FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_NAME = '{table}'
    """)
    columns = cursor.fetchall()
    if columns:
        js_data.append(f"  dimensions: {{")
        for row in columns:
            column_name = make_unique_name(used_names, row.COLUMN_NAME.lower())
            data_type = (
                'number' if row.DATA_TYPE in ['int', 'bigint', 'smallint', 'tinyint', 'bit', 'decimal', 'numeric', 'float', 'real', 'money'] 
                else 'time' if row.DATA_TYPE in ['datetime', 'date', 'time', 'timestamp'] 
                else 'string'
            )
            primary_key = "primary_key: true," if row.COLUMN_NAME.lower().endswith("id") else ""
            js_data.append(f"    {column_name}: {{")
            js_data.append(f"      sql: `{row.COLUMN_NAME}`,")
            js_data.append(f"      type: `{data_type}`,")
            if primary_key:
                js_data.append(f"      {primary_key}")
            js_data.append(f"    }},")
        js_data.append(f"  }},")

    # Measures
    js_data.append(f"  measures: {{")
    js_data.append(f"    count: {{")
    js_data.append(f"      type: `count`")
    js_data.append(f"    }},")
    numeric_columns = [col.COLUMN_NAME for col in columns if col.DATA_TYPE in ['int', 'bigint', 'smallint', 'tinyint', 'bit', 'decimal', 'numeric', 'float', 'real', 'money']]
    for column in numeric_columns:
        sum_name = make_unique_name(used_names, f"sum_{column.lower()}")
        avg_name = make_unique_name(used_names, f"avg_{column.lower()}")
        js_data.append(f"    {sum_name}: {{")
        js_data.append(f"      sql: `SUM({column})`,")
        js_data.append(f"      type: `number`")
        js_data.append(f"    }},")
        js_data.append(f"    {avg_name}: {{")
        js_data.append(f"      sql: `AVG({column})`,")
        js_data.append(f"      type: `number`")
        js_data.append(f"    }},")
    js_data.append(f"  }},")

    # Pre-aggregations (if needed)
    js_data.append(f"  pre_aggregations: {{")
    js_data.append(f"    // Pre-aggregation definitions go here.")
    js_data.append(f"    // Learn more in the documentation: https://cube.dev/docs/caching/pre-aggregations/getting-started")
    js_data.append(f"  }}")

    js_data.append(f"}});")

    # Write to .js file
    file_path = os.path.join(output_dir, f'{table}.js')
    with open(file_path, 'w') as file:
        file.write('\n'.join(js_data))

conn.close()
