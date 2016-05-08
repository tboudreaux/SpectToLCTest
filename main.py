from astropy.io import fits
import matplotlib.pyplot as plt
import numpy as np
import jdcal


def fitfunction(degree, wavelength, flux, offset, zuma):
    # two lists for later use in the function
    newwave = []
    newflux = []
    # ignored Hydrogen alpha and beta, this will latter be turned into a profile thing, using more or less the same
    # code used in ccor, however for now this works
    for j in range(len(wavelength)):
        if (wavelength[j] >= 4855 and wavelength[j] <= 4867) or (wavelength[j] >= 6554 and wavelength[j] <= 6570):
            pass
        if zuma is True:
            if 6677 <= wavelength[j] <= 6679:
                pass
            else:
                newwave.append(wavelength[j])
                newflux.append(flux[j])
        else:
            newwave.append(wavelength[j])
            newflux.append(flux[j])
    # typecats BECAUSE I CAN, also BECAUSE IT NEEDS TO HAPPEN FOR CODE TO RUN
    degree = int(degree)
    # bear with me for the section, its kinda jankey
    # Fits a function z to the data with highest exponent degree
    z = np.polyfit(newwave, newflux, degree)
    # creats a function f which is z(something)
    f = np.poly1d(z)
    # creates all the y values for the function fit
    y_poly = f(newwave)
    # divides out the function fit to the flux to normalize it
    y_new = newflux / y_poly
    # for kicks
    y_fit = y_new
    # standard deviation and mean of the normalized flux
    fluxstdev = np.std(y_new)
    mean = np.mean(y_new)
    forrange = len(y_new)
    # this loop removes all values more than 3 sigma away from the mean, that will become user definable, it ignores
    # all values more than 3 sigma from the mean, removing those that are greater than the mean, (since they are
    # mostlikely cosimic rays) and just ignoring those that are below the mean
    for i in range(forrange):
        if y_new[i] >= (3 * fluxstdev) + mean:
            y_new[i] = mean
            y_fit[i] = mean
        if y_new[i] <= mean - (3 * fluxstdev):
            y_fit[i] = mean
    # this reintroduces the trend into the data (now with outlies removed)
    flux2 = y_fit * y_poly
    # goes threw the prosses of refitting the curve to the data sans outliers now
    z = np.polyfit(newwave, flux2, degree)
    f = np.poly1d(z)
    y_poly = f(wavelength)
    y_new = flux / y_poly
    # I honesetly don't know what this does any more, I will figure that out at some point (this is why
    # I need to get better at commenting b/c I wrote that like a week ago, but I don't know why I wrote that)
    for i in range(forrange):
        if y_new[i] >= (3 * fluxstdev) + mean:
            y_new[i] = mean
    # appled an artificial offset to the flattened data so that it can be seen better
    if offset != 0:
        for j in range(len(y_new)):
            y_new[j] += offset
    # returnes a dictionary of values, dictionary returns are the best and should be more widely known
    return {'y_poly': y_poly, 'y_new': y_new, 'wave': wavelength}


targetpath = raw_input('Please enter the path to the target file: ')
targetfile = open(targetpath, 'rb')
targetfile = targetfile.readlines()
targetfile = [x.strip() for x in targetfile]
date = []
brightness = []
for i in range(len(targetfile)):
    fitsfile = fits.open(targetfile[i])
    date.append(fitsfile[0].header['UTSHUT'])
    Area = 0
    for j in range(62):
        wavelength = np.float64(fitsfile[0].data[j, :, 0])
        flux = np.float64(fitsfile[0].data[j, :, 1])
        fitdate = fitfunction(4, wavelength, flux, 0, False)
        subarea = 0
        for k in range(len(wavelength)):
            subarea += wavelength[k] * fitdate['y_new'][k]
        Area += subarea
    brightness.append(Area)
maxb = 0
index = 0
for i in range(len(brightness)):
    if brightness[i] > maxb:
        maxb = brightness[i]
        print maxb
        index = i
    else:
        pass
pb = [None] * len(brightness)
for i in range(len(brightness)):
    differnce = maxb - brightness[i]
    percentdiff = differnce/brightness[i]
    percentbright = 1 - percentdiff
    pb[i] = percentbright
# minbrightness = min(brightness)
# brightness = [(x-minbrightness) + 1 for x in brightness]
print pb
print date


