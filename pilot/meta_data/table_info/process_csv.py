import pandas as pd
import os 
os.chdir('/home/vincent/work/DB-GPT/pilot/meta_data/table_info/')
# Read the CSV files
csv1 = pd.read_csv('table.csv')
csv2 = pd.read_csv('tablecol.csv')

# Convert the 'create_time' and 'update_time' columns to datetime
csv1['create_time'] = pd.to_datetime(csv1['create_time'])
csv1['update_time'] = pd.to_datetime(csv1['update_time'])

# Filter the records in csv1 based on your criteria
latest_records = csv1.groupby('table_name').apply(
    lambda group: group[group['table_comment'].notna()].nlargest(1, 'update_time') if group['table_comment'].notna().any() else group.nlargest(1, 'update_time')
)

# Reset the index while dropping the existing index
latest_records = latest_records.reset_index(drop=True)
# Merge the filtered data from both CSVs on the 'table_name' column
merged_data = pd.merge(latest_records, csv2, on='table_name')

# Group the merged data by database and table name
grouped_data = merged_data.groupby(['database_name', 'table_name'])

# Initialize an empty dictionary to store the DDL SQL statements
ddl_sql_statements = {}

# database_name, table_name, column_name, column_type, column_comment, table_comment, all_comment, ddl_sql
df_table_col_clean = []


# Iterate through the grouped data and create DDL statements
for (db_name, table_name), group_data in grouped_data:
    column_names = ''
    column_types = ''
    column_comments = ''
    table_comment = ''
    ddl_sql = f"CREATE TABLE {db_name}.{table_name} (\n"
    for _, row in group_data.iterrows():
        table_comment = row['table_comment']
        column_name = row['column_name']
        column_type = row['column_type']
        column_comment = row['column_comment']
        column_names += column_name + '\t'
        column_types += column_type + '\t'
        column_comments += str(column_comment) + '\t'
        if pd.isna(column_comment):
            ddl_sql += f"    {column_name} {column_type},\n"
        else:
            ddl_sql += f"    {column_name} {column_type} COMMENT '{column_comment}',\n"
    ddl_sql = ddl_sql.rstrip(',\n')  # Remove the trailing comma and newline
    ddl_sql += f"\n)"
    if table_comment:
        ddl_sql += f" COMMENT '{table_comment}'"
    ddl_sql += ';'
    ddl_sql_statements[f'{db_name}.{table_name}'] = ddl_sql
    all_comment = f"{db_name}.{table_name} {table_comment} {column_comment.replace('?','').replace('nan','')}"
    all_comment_col_name = f"{db_name}.{table_name} {table_comment} {column_comment[:-1].replace('?','').replace('nan','')} {column_names[:-1]}"
    df_table_col_clean.append([db_name, table_name, column_names[:-1],column_types[:-1],column_comments[:-1],table_comment,all_comment,all_comment_col_name,ddl_sql])
df_table_col_clean = pd.DataFrame(df_table_col_clean,
                                  columns=['database_name', 'table_name', 'column_name', 'column_type', 'column_comment', 
                                           'table_comment', 'all_comment', 'all_comment_col_name', 'ddl_sql'])
df_table_col_clean.to_csv('df_table_col_clean.csv')

# Print or save the DDL SQL statements as per your requirement
# for key, value in ddl_sql_statements.items():
#     print(f"DDL SQL for {key}:\n{value}")
