import mysql.connector
import time

suppress_db = 0

if not suppress_db:
    my_db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="document_reconciliation"
    )
    my_cursor = my_db.cursor()


def save_docs(doc_id, content, title):
    if suppress_db:
        return
    now = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())
    sql = """INSERT INTO
                docs (`id`, `title`, `upload_date`, `original_json`)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                `title` = VALUES(`title`),
                `original_json` = VALUES(`original_json`)"""
    val = (doc_id, title, now, content)
    my_cursor.execute(sql, val)


def save_flags(doc_id, flags):
    if suppress_db:
        return
    now = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())
    sql = """DELETE FROM flags WHERE `doc_id` = %s;"""
    my_cursor.execute(sql, (doc_id,))
    for f in flags:
        sql = """INSERT INTO
                    flags (`doc_id`, `flag`, `set_date`)
                    VALUES (%s, %s, %s)"""
        val = (doc_id, f, now)
        my_cursor.execute(sql, val)


def commit():
    if suppress_db:
        return
    my_db.commit()
