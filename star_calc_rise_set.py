#! /usr/bin/env python

# Calculates the rise and set times of a star and the star's position given the right ascension & declination
import datetime
import numpy as np
from astro_date_unit_fcns import *

# some defaults
default_dt = datetime.datetime(1988, 3, 20, 0, 0)
sf_lat = 38.3047
sf_longitude = 122.2989
rt_asc_arturus = 213.9167
dec_arturus = 19.1822

def star_rise_set(dt_input=default_dt, rt_asc=rt_asc_arturus, dec=dec_arturus, lat=sf_lat, longitude=sf_longitude, starq=1):
    """
    RISE, TRANSIT, SET = star_rise_set(DATETIME Object, RIGHT ASCENSION, DECLINATION, LATITUDE, LONGITUDE, STARQ)
    For a specific star return the rise, transit and set times
    All inputes, except the datetime object, are assumed to be in degrees
    If STARQ == 0, then the calculations will be done for the Sun

    The outputs are in UT time! Not sidereal time.
    The outputs are datetime objects.

    These calculations were taken from Chapter 15 of Astronomy Algorithms
    """
    # an input needed for the math below
    h0_star = -0.5667
    h0_sun = -0.8333
    if starq == 1:
        h0 = h0_star
    elif starq == 0:
        h0 = h0_sun
    else:
        print "Error: input not recognized"
    
    # calculate sidereal time in greenwich at 0 UT
    day_only = datetime.datetime.combine(dt_input.date(), datetime.time(0))
    sidereal_time = sidereal_time_greenwich(day_only)
    # convert inputs into radians
    h0_rad = np.radians(h0)
    lat_rad = np.radians(lat)
    longitude_rad = np.radians(longitude)
    rt_asc_rad = np.radians(rt_asc)
    dec_rad = np.radians(dec)
    sidereal_time_rad = np.radians(sidereal_time)

    # do the math
    cos_H0 = (np.sin(h0_rad)-(np.sin(lat_rad)*np.sin(dec_rad))) / (np.cos(lat_rad)*np.cos(dec_rad))
    if cos_H0 < -1 or cos_H0 > 1:
        print 'Error: this could be a circumpolar star'
    H0 = np.degrees(np.arccos(cos_H0))

    # transit, rise & set in degrees - make sure they a between 0 & 360
    transit_deg = (rt_asc + longitude - sidereal_time)
    rise_deg = (transit_deg - H0)
    set_deg = (transit_deg + H0)
    # let's see if the transit or set times are actually happening the next day
    transit_day = 0
    rise_day = 0
    set_day = 0
    # transit check
    if transit_deg>360:
        transit_day = 1
        transit_deg = transit_deg % 360
    elif transit_deg<0:
        transit_day = -1
        transit_deg = transit_deg % 360
    # rise check
    if rise_deg>360:
        rise_day = 1
        rise_deg = rise_deg % 360
    elif rise_deg<0:
        rise_day = -1
        rise_deg = rise_deg % 360
    # set check
    if set_deg>360:
        set_day = 1
        set_deg = set_deg % 360
    elif set_deg<0:
        set_day = -1
        set_deg = set_deg % 360

    # change the degrees into datetime objects
    transit_dt = datetime.datetime.combine(dt_input.date(), decdeg2time(transit_deg).time())
    rise_dt = datetime.datetime.combine(dt_input.date(), decdeg2time(rise_deg).time())
    set_dt = datetime.datetime.combine(dt_input.date(), decdeg2time(set_deg).time())
    # add a day if we need to
    transit_dt = transit_dt + datetime.timedelta(days=transit_day)
    rise_dt = rise_dt + datetime.timedelta(days=rise_day)
    set_dt = set_dt + datetime.timedelta(days=set_day)
    return transit_dt, rise_dt, set_dt

def timezone_change(dt_input):
    # this only converts UT time to PDT/PST for right now
    # *** HACK *** these dates only work for 2015, need to find the right sunday for other years
    # does not take into account the fact the dst begins/ends at 2am
    daylight_beg = datetime.datetime(dt_input.year, 3, 8, 0)
    daylight_end = datetime.datetime(dt_input.year, 11, 1, 0)
    hrs = -8
    if dt_input >= daylight_beg and dt_input < daylight_end:
        hrs = -7
    return dt_input + datetime.timedelta(hours=hrs)

def display_arturus_example():
    # display some example results
    # the right ascension of the transit time does match now
    # you can verify by inputing the "transit_time" into this webpage:
    # http://www.csgnetwork.com/siderealjuliantimecalc.html
    # the LST result should be equal to the right ascension

    # first pull in the default results, these are in degrees in Greenwich timezone
    transit, rise, setting = star_rise_set(datetime.datetime.utcnow())

    # need to convert the UT time to local time
    # should use the pytz package for this instead
    transit_local = timezone_change(transit)
    rise_local = timezone_change(rise)
    set_local = timezone_change(setting)

    # print out some results
    print 'Here are the results for Arcturus in SF local time today:'
    print 'Rise time: ' + rise_local.time().isoformat()
    print 'Transit time: ' + transit_local.time().isoformat()    
    print 'Set time: ' + set_local.time().isoformat()

def main():
    display_arturus_example()

if __name__ == '__main__':
    main()
