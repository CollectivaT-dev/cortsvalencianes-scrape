# Corts Valencianes Scrape
Processes to scrape cortsvalencianes.es and generate a speech dataset.

## Pipeline (currently)

Scrape process currently works in steps, which seperate scripts are launched for each. The results are currently saved in a file rather than a db.


* `scrape_corts.py`: Scrapes the list of sessions from the search page and puts it in `items.json` file
* `download.py`: Uses the `items.json` information to choose the plenary sessions and download the relevant videos from the streaming source
* `generate_diaris.py`: From the list of plenary sessions in `items.json`, generates the transcript links and saves it to `items_diaris.json`.

## Install and launch

Install the requirements via virtualenv
```
virtualenv --python=python venv
sourve venv/bin/activate
```

Currently the scripts are launched one after the other without any parameters. The only requirement is that `scrape_corts.py` has to come first.
```
python scrape_corts.py
python download.py
python generate_diaris.py 
```

## Tasks to do:

* [] fix download.py for continuous download
* [x] fix generate diaris
* [x] match diaris with videos
* [x] scrape speakers and timestamps for each intervention in a session
* [] write diari parser in speaker, intervention format
* [] structure output for `long-audio-alignment` format
* [] persist in a db
