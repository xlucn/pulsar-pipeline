#!/usr/bin/env python
import os
import csv
import numpy as np
import matplotlib.pyplot as plt


if __name__ == '__main__':
    resultdir = "result"
    outputdir = os.path.join(resultdir, "output")
    plotdir = os.path.join(resultdir, "plots")
    if not os.path.exists(plotdir):
        os.mkdir(plotdir)

    with open("filterdata.csv") as f:
        for source in csv.DictReader(f):
            name = source['JName']
            plt.title(name)
            plt.xscale('log')
            plt.yscale('log')
            plt.xlabel('$E$  ($m_ec^2/\\mathrm{s}$)')
            plt.ylabel('flux')
            for txt in os.listdir(outputdir):
                if txt.startswith(name):
                    # filter data below floating point precision
                    E, flux = np.loadtxt(os.path.join(outputdir, txt)).T
                    plt.plot(E[flux > 1e-308], flux[flux > 1e-308])
            plt.savefig(os.path.join(plotdir, "{}.eps".format(name)))
            plt.close()