import sqlite3

from flask import Flask, request, jsonify
from typing import Dict
import json
import pygeohash

app = Flask(__name__)
DATABASE_NAME = 'webhook_data.db'


def init_db() -> None:
    """
    Initiation script for the SQLite database. Currently just 
    creates a table with a single text field but feel free to modify
    this as required for your solution below.
    """
    with sqlite3.connect(DATABASE_NAME) as conn:
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS webhook_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                payload TEXT
            )
        """)
        conn.commit()


@app.route('/webhook-endpoint', methods=['POST'])
def webhook_listener():
    try:
        data = request.json
        handle_webhook(data)

        return jsonify({"message": "Data received successfully!"}), 200
    except Exception as e:
        print(f"Error occurred: {e}")
        return jsonify({"error": "Failed to decode data."}), 400


def handle_webhook(data: Dict[str, any]) -> None:
    """
    Process the data as required. In this case, we're just printing it.

    Instructions:
    Write a function that handles the incoming webhooks and places them into
    a SQLite database. Treat this database like you would a RAW layer in a 
    warehouse like Snowflake/Redshift.
    """

    print("Received webhook data:", data)

    if data:
        event_type = data.get("type")
        location = data.get("location")

        if location:
            if location.get("type").lower() == "point":
                coordinates = location.get("coordinates")
                lat, lon = coordinates.get("latitude"), coordinates.get("longitude")
                geohash = pygeohash.encode(float(lat), float(lon))
                location.update({"geohash": geohash})

        json_string = json.dumps(data)

        if event_type.lower() == "user.entered_geofence":
            publish_custom_event_to_kinesis(json_string)

        # avoiding string templating as they are prone to sql injection
        # see https://pythonassets.com/posts/reproducing-sql-injection-in-sqlite3-and-pymysql/

        # we're ingesting the json as STRING/TEXT in the raw table in our warehouse.
        # we will use transformations inside the warehouse to organize our data
        # ingesting as TEXT allows to view bad records in case of poor data quality at source
        # with a tradeoff i.e. a bit more compute resources are utilized in the data warehouse
        # although transforming data in lamda/serverless will also utilize compute capacity

        # POV: Clang is faster than python, therefore databases(e.g. postgres) are written in C and
        #      will process data quicker than python ever will even with Cython.

        # snowflake connection can also be configured here instead of sqlite.
        with sqlite3.connect(DATABASE_NAME) as conn:
            c = conn.cursor()
            c.execute("""
                insert into webhook_data (payload)
                values(?);
            """, [json_string])
            conn.commit()


def publish_custom_event_to_kinesis(data):
    # Implement a custom publish event to kinesis or pub/sub (can be applied to entry/exit)

    print("eg: entered_geofence")
    # import boto3
    #
    # kinesis_client = boto3.client(
    #     'kinesis',
    #     region_name = '<region>',
    #     aws_access_key_id = '<super-secret-key-id>',
    #     aws_access_key_secret = '<super-secret>'
    # )
    #
    # kinesis_client.put_record(
    #     StreamName='<stream-name>',
    #     Data=data,
    #     PartitionKey='<your-uuid>'
    # )


if __name__ == "__main__":
    init_db()
    app.run(port=65530)
