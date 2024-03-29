#!/usr/bin/env python
# NOTE: The whole database could also be downloaded from website:
# https://www.atnf.csiro.au/research/pulsar/psrcat/download.html
import os
import csv
import logging
import argparse
import requests
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO, format="%(filename)s: %(message)s")


def request_data(coor1, coor2, r):
    baseurl = "https://www.atnf.csiro.au/research/pulsar/psrcat/proc_form.php"
    parameters = {
        "version": "1.62",
        "JName": "JName",
        "Dist": "Dist",
        "Age": "Age",
        "Edot": "Edot",
        "RaJD": "RaJD",
        "DecJD": "DecJD",
        "startUserDefined": "true",
        "sort_attr": "jname",
        "sort_order": "asc",
        "condition": "",
        "ephemeris": "short",
        "coords_unit": "rajd/decjd",
        "radius": r,
        "coords_1": coor1,
        "coords_2": coor2,
        "style": "Short csv without errors",
        "no_value": "*",
        "fsize": "3",
        "x_axis": "",
        "x_scale": "linear",
        "y_axis": "",
        "y_scale": "linear",
        "state": "query",
        "table_bottom.x": "29",
        "table_bottom.y": "21"
    }

    try:
        res = requests.get(baseurl, params=parameters)
    except (requests.exceptions.ConnectionError,
            requests.exceptions.ConnectTimeout):
        logging.error("Connection error, please re-run the script")
        exit(1)

    if res:
        soup = BeautifulSoup(res.content, 'html.parser')
        rawdata = soup.find("pre").string.strip() + '\n'
    else:
        logging.error("Download failed, please re-run the script")
        exit(1)

    return rawdata


def save_data(rawdata):
    rawdata_file = os.path.join(resultdir, "rawdata.csv")
    data_file = os.path.join(resultdir, "data.csv")
    with open(rawdata_file, "w") as f:
        f.write(rawdata)

    with open(rawdata_file) as rawdata, open(data_file, "w") as f:
        count = 0
        fields = ['JName', 'Age', 'Dist', 'Edot', 'RaJD', 'DecJD']
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for data in csv.DictReader(rawdata, delimiter=';'):
            if not data['#']:
                continue
            count += 1
            RaJD = float(data['RAJD'])
            DecJD = float(data['DECJD'])
            if data['DIST'] != '*' and data['AGE'] != '*' \
                    and data['EDOT'] != '*':
                # convert unit from erg/s to m_e c^2/s
                Edot = float(data['EDOT']) * 1221432.8760283517
                # convert unit from kpc to pc
                Dist = float(data['DIST']) * 1e3
                # convert unit from yr to s
                Age = float(data['AGE']) * 365.25 * 24 * 60 * 60

                writer.writerow({'JName': data['PSRJ'],
                                 'Age': Age, 'Dist': Dist, 'Edot': Edot,
                                 'RaJD': RaJD, 'DecJD': DecJD})
            else:
                Edot = data['EDOT']
                Dist = data['DIST']
                Age = data['AGE']
                writer.writerow({'JName': data['PSRJ'],
                                 'Age': Age, 'Dist': Dist, 'Edot': Edot,
                                 'RaJD': RaJD, 'DecJD': DecJD})
        logging.info("Data saved!")
        logging.info("Total: %d" % (count))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--coor', nargs=2, metavar=("Ra/deg", "Dec/deg"))
    parser.add_argument('-r', '--radius', nargs=1, metavar="Radius/deg")
    args = parser.parse_args()

    if not 0 < float(args.coor[0]) < 360:
        logging.error("<ra> should be within (0, 360) degrees")
        exit(1)
    if not -90 < float(args.coor[1]) < 90:
        logging.error("<dec> should be within (-90, 90) degrees")
        exit(1)

    currentdir = os.path.dirname(__file__)
    resultdir = os.path.join(currentdir, "result")
    if not os.path.exists(resultdir):
        os.mkdir(resultdir)

    rawdata = request_data(args.coor[0], args.coor[1], args.radius)
    save_data(rawdata)
