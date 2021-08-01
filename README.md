# INTRODUCTION

This page will give the details about tap and target of an ETL pipeline which does historical and incremental loading of sunrise and sunset details of Pune (Maharashtra, India)

## SETTING UP ENVIRONMENT FOR TAP
The template of the tap is taken from [here](https://github.com/singer-io/singer-tap-template).

You can do the setup as follows

For linux : 
```shell
cd tap-sunrise-sunset
python3 -m venv ~/.virtualenvs/tap-sunrise-sunset
source ~/.virtualenvs/tap-sunrise-sunset/bin/activate
pip install -e .
deactivate
```

For windows : 

```shell
python -m venv virtualenvs/tap-sunrise-sunset
.\virtualenvs\tap-sunrise-sunset\Scripts\activate
cd tap-sunrise-sunset
pip install -e .
deactivate
```

## SETTING UP ENVIRONMENT FOR TARGET

The target is taken from [here](https://gitlab.com/meltano/target-sqlite)

You can do the setup for target as follows

For linux:

```shell
cd target-sqlite-master
python3 -m venv ~/.virtualenvs/target-sqlite-master
source ~/.virtualenvs/target-sqlite-master/bin/activate
pip install -e '.[dev]'
deactivate
```

For windows:

```shell
python -m venv virtualenvs/target-sqlite-master
.\virtualenvs\target-sqlite-master\Scripts\activate
cd target-sqlite-master
pip install -e '.[dev]'
deactivate
```

## RUNNING THE TAP AND TARGET

The config for tap is `tap_sunrise_sunset/config.json` and config for target is `target-sqlite-master/config.json`.

Users have 2 options that is load the historical data or load the incremental data.

- Historical Load : loads historical data. The default start date is 1st Jan 2020.
- Incremental Load : Append today’s data in existing target

### LOADING THE HISTORICAL DATA

Run the following command to load the historical data
(will load the date from 1st Jan 2020 to current date)

For linux:
```shell
~/.virtualenvs/tap-sunrise-sunset/bin/tap-sunrise-sunset --config tap_sunrise_sunset/config.json | ~/.virtualenvs/target-sqlite-master/bin/target-sqlite -c target-sqlite-master/config.json 
```

For windows:
```shell
.\virtualenvs\tap-sunrise-sunset\Scripts\tap-sunrise-sunset.exe --config .\tap-sunrise-sunset\config.json | .\virtualenvs\target-sqlite-master\Scripts\target-sqlite.exe -c .\target-sqlite-master\config.json
```

After running this  `state.json` and `sunrise_sunset.db` files will be created. The `state.json` will store the date till which the data was loaded.

A sample `state.json` looks like this

```json
{
    "end_date": "2021-06-13"
}
```

### LOADING THE INCREMENTAL DATA

If a user wants to load incremental data, the user should give the `state.json` filepath as input (that was created while loading the historical data) in the following way:

For linux:
```shell
~/.virtualenvs/tap-sunrise-sunset/bin/tap-sunrise-sunset --config tap-sunrise-sunset/config.json --state state.json | ~/.virtualenvs/target-sqlite-master/bin/target-sqlite -c target-sqlite-master/config.json 
```

For windows:
```shell
.\virtualenvs\tap-sunrise-sunset\Scripts\tap-sunrise-sunset.exe --config .\tap-sunrise-sunset\config.json --state .\state.json | .\virtualenvs\target-sqlite-master\Scripts\target-sqlite.exe -c .\target-sqlite-master\config.json
```

The date stored in `state.json` will be used as starting date and data will retrieved till the current date. After running this, `sunrise_sunset.db` will get updated with new incremental data and also `state.json` will get udpated with current_date.

### LOADING EVERYDAY DATA

Only for the first time, user has to run the historical data. Then for every day he can run the incremental load to load the data for that day.Before running incremental data he has to run historical data atleast once. You need to setup tap and target only for the first time.
