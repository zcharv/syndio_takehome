import sqlite3

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from sqlalchemy import create_engine, text

import statsmodels.api as sm
import logging
import pandas as pd

logging.basicConfig(filename="exceptions.log")
logger = logging.getLogger(__name__)

app = FastAPI()
DATABASE = 'employees.db'
TABLE_NAME = 'employees'
NEW_TABLE_NAME = 'employees_copy'


def copy_table_and_update(engine):
    try:
        with engine.begin() as conn:
            conn.execute(
                text(f'CREATE TABLE IF NOT EXISTS {NEW_TABLE_NAME} AS SELECT * FROM {TABLE_NAME}')
            )
            conn.execute(
                text(f'UPDATE {NEW_TABLE_NAME} SET protected_class="1" WHERE protected_class="reference"')
            )
            conn.execute(
                text(f'UPDATE {NEW_TABLE_NAME} SET protected_class="0" WHERE protected_class="comparison"')
            )
    except Exception as e:
        logger.exception(e)
        return JSONResponse(
            status_code=500,
            content={"error": 'issue coping employee table and updating values'},
        )
    finally:
        conn.close()


@app.get("/")
@app.get("/pvalue/{department}")
async def get_pvalue(department):
    independent_vars = ['protected_class', 'tenure', 'performance']
    dependent_var = 'compensation'
    vars_str = ", ".join(field for field in independent_vars)
    vars_str += f', {dependent_var}'

    engine = create_engine(f"sqlite:///{DATABASE}")
    copy_table_and_update(engine)
    try:
        with engine.connect() as conn, conn:
            data = pd.read_sql_query(f'SELECT {vars_str} FROM {NEW_TABLE_NAME} WHERE department LIKE "{department}";',
                                     conn)
    except Exception as e:
        logger.exception(e)
        return JSONResponse(
            status_code=500,
            content={"error": 'issue querying employee database'},
        )
    finally:
        conn.close()

    X = data[independent_vars]
    Y = data[dependent_var]

    X = sm.add_constant(X)

    try:
        reg = sm.OLS(Y, X.astype(float)).fit()
    except Exception as e:
        logger.exception(e)
        return JSONResponse(
            status_code=500,
            content={"error": 'issue generating regression'},
        )

    out = round(reg.pvalues['protected_class'], 3)

    return JSONResponse(
        status_code=200,
        content={"pvalue": out},
    )
