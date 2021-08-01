#!/usr/bin/env python3
import os
import json
import time
import singer
import datetime
import requests
import argparse
from dateutil import tz
from singer import utils, metadata
from singer.catalog import Catalog, CatalogEntry
from singer.schema import Schema


REQUIRED_CONFIG_KEYS = ["start_date", "username", "password"]
LOGGER = singer.get_logger()


def get_abs_path(path):
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), path)


def load_schemas():
    """ Load schemas from schemas folder """
    schemas = {}
    for filename in os.listdir(get_abs_path('schemas')):
        path = get_abs_path('schemas') + '/' + filename
        file_raw = filename.replace('.json', '')
        with open(path) as file:
            schemas[file_raw] = Schema.from_dict(json.load(file))
    return schemas

def discover():
    raw_schemas = load_schemas()
    streams = []
    for stream_id, schema in raw_schemas.items():
        # TODO: populate any metadata and stream's key properties here..
        stream_metadata = []
        key_properties = []
        streams.append(
            CatalogEntry(
                tap_stream_id=stream_id,
                stream=stream_id,
                schema=schema,
                key_properties=key_properties,
                metadata=stream_metadata,
                replication_key=None,
                is_view=None,
                database=None,
                table=None,
                row_count=None,
                stream_alias=None,
                replication_method=None,
            )
        )
    return Catalog(streams)


def sync(config, state, catalog):
    """ Sync data from tap source """
    # Loop over selected streams in catalog
    for stream in catalog.get_selected_streams(state):
        LOGGER.info("Syncing stream:" + stream.tap_stream_id)

        bookmark_column = stream.replication_key
        is_sorted = True  # TODO: indicate whether data is sorted ascending on bookmark value

        singer.write_schema(
            stream_name=stream.tap_stream_id,
            schema=stream.schema,
            key_properties=stream.key_properties,
        )

        # TODO: delete and replace this inline function with your own data retrieval process:
        tap_data = lambda: [{"id": x, "name": "row${x}"} for x in range(1000)]

        max_bookmark = None
        for row in tap_data():
            # TODO: place type conversions or transformations here

            # write one or more rows to the stream:
            singer.write_records(stream.tap_stream_id, [row])
            if bookmark_column:
                if is_sorted:
                    # update bookmark to latest value
                    singer.write_state({stream.tap_stream_id: row[bookmark_column]})
                else:
                    # if data unsorted, save max value until end of writes
                    max_bookmark = max(max_bookmark, row[bookmark_column])
        if bookmark_column and not is_sorted:
            singer.write_state({stream.tap_stream_id: max_bookmark})
    return

def read_json(path):
    with open(path, 'r') as f:
        data = json.load(f)
    return data

def convert_utc_to_ist(datetimestr, from_zone=tz.gettz('UTC'), to_zone=tz.gettz('Asia/Kolkata')):
    utc = datetime.datetime.strptime(datetimestr, "%Y-%m-%dT%H:%M:%SZ")
    utc = utc.replace(tzinfo=from_zone)
    ist = utc.astimezone(to_zone)
    # converting to string and removing +05:30 from it
    ist = str(ist)[:-6]
    return ist

def get_data_from_api(config, start_date, end_date):
    response = requests.get(
                                config["api_link"],
                                params={
                                    'latitude': config["latitude"],
                                    'longitude': config["longitude"],
                                    'start': str(start_date),
                                    'end': str(end_date)
                                },
                                headers={
                                    'x-api-key': config["api_key"]
                                }
        )
    # wait for 1 seconds after that process the messgae
    time.sleep(1)
    # retrieve the data
    data = response.json()
    try:
        # there are two keys meta and data. data contains all the information.
        return data['data']
    except:
        # no keys implies request limit is exceeded
        return []

@utils.handle_top_exception(LOGGER)
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--state', help="path to state.json file", required=False)
    parser.add_argument('--config', help="path to config.json file", required=True)
    arguments = vars(parser.parse_args())

    schemas = load_schemas()
    singer.write_schema('features', schemas.get('features').to_dict(), 'date')

    # reading config
    config = read_json(arguments['config'])

    if arguments['state'] is None:
        # user not giving state.json, so we will consider from first
        start_date = datetime.date(2020, 1, 1)
    else:
        # if state.json is passed we will consider that as the start_date
        loaded_state = read_json(arguments['state'])
        
        start_date = loaded_state['end_date']
        # this will return datetime object, so I am converting it to date.
        start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d").date() + datetime.timedelta(days=1)

    end_date = datetime.date.today()
    
    # the api has only 100 days limit betwen start and end
    if (end_date - start_date) > datetime.timedelta(days=100):
        flag = 0
        new_start_date = start_date
        new_end_date = start_date + datetime.timedelta(days=100)
        data = []
        while(new_start_date <= end_date):
            period_data = get_data_from_api(config, new_start_date, new_end_date)
            # adding the new one with previous one.
            data.extend(period_data)
            new_start_date = new_end_date + datetime.timedelta(days=1)            
            new_end_date = new_start_date + datetime.timedelta(days=100)
            if new_end_date > end_date:
                new_end_date = end_date
    else:
        data = get_data_from_api(config, start_date, end_date)

    output_data = []
    for one_day_data in data:
        required = {}
        required['date'] = one_day_data['date']
        required['sunriseStart'] = convert_utc_to_ist(one_day_data['sunriseStart'])
        required['sunriseEnd'] = convert_utc_to_ist(one_day_data['sunriseEnd'])
        required['sunsetStart'] = convert_utc_to_ist(one_day_data['sunsetStart'])
        required['sunsetEnd'] = convert_utc_to_ist(one_day_data['sunsetEnd'])
        output_data.append(required)
    
    singer.write_records('features', output_data)
    # output state.json file
    state = {
                "end_date": str(end_date)
            }

    if arguments['state'] is None:
        with open("state.json", 'w') as f:
            json.dump(state, f, indent=4)
    else:
        with open(arguments['state'], 'w') as f:
            json.dump(state, f, indent=4)

if __name__ == "__main__":
    main()
