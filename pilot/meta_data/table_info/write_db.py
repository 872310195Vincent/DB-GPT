
import sys
import os
# 将pilot模块所在的路径添加到sys.path
pilot_path = '/home/vincent/work/DB-GPT/'  # 替换成pilot模块的实际路径
sys.path.append(pilot_path)



from sqlalchemy import create_engine
import pymysql
import pandas as pd
from urllib.parse import quote

from pilot.configs.config import Config

CFG = Config()

tableName   = "table_info"
dataFrame   = pd.read_csv('/home/vincent/work/DB-GPT/pilot/meta_data/table_info/df_table_col_clean.csv')
for vector_table_info in dataFrame['all_comment_col_name']:
    table_name = vector_table_info.split(' ')[0]
    print(table_name)
    print(vector_table_info)

# sqlEngine       = create_engine(
#         f"mysql+pymysql://"
#         + quote(CFG.LOCAL_DB_USER)
#         + ":"
#         + quote(CFG.LOCAL_DB_PASSWORD)
#         + "@"
#         + CFG.LOCAL_DB_HOST
#         + ":"
#         + str(CFG.LOCAL_DB_PORT)
#         + f"/dbgpt"
#     )
# dbConnection    = sqlEngine.connect()
# print(dataFrame)
# try:
#     frame           = dataFrame.to_sql(tableName, dbConnection, if_exists='replace');
# except ValueError as vx:
#     print(vx)
# except Exception as ex:   
#     print(ex)
# else:
#     print("Table %s created successfully."%tableName);   
# finally:
#     dbConnection.close()