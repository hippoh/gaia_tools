###############################################################################
# tgasSelect.py: Selection function for (part of) the TGAS data set
###############################################################################
###############################################################################
#
# This file contains routines to compute the selection function of subsets
# of the Gaia DR1 TGAS data. As usual, care should be taken when using this
# set of tools for a subset for which the selection function has not been 
# previously tested.
#
# The basic, underlying, complete set of 2MASS counts was generated by the 
# following SQL query (applied using Python tools):
#
"""
select floor((j_m+(j_m-k_m)*(j_m-k_m)+2.5*(j_m-k_m))*10), \
floor((j_m-k_m+0.05)/1.05*3), floor(hp12index/16384), count(*) as count \
from twomass_psc, twomass_psc_hp12 \
where (twomass_psc.pts_key = twomass_psc_hp12.pts_key \
AND (ph_qual like 'A__' OR (rd_flg like '1__' OR rd_flg like '3__')) \
AND (ph_qual like '__A' OR (rd_flg like '__1' OR rd_flg like '__3')) \
AND use_src='1' AND ext_key is null \
AND (j_m-k_m) > -0.05 AND (j_m-k_m) < 1.0 AND j_m < 13.5 AND j_m > 4) \
group by floor((j_m+(j_m-k_m)*(j_m-k_m)+2.5*(j_m-k_m))*10), \
floor((j_m-k_m+0.05)/1.05*3),floor(hp12index/16384) \
order by floor((j_m+(j_m-k_m)*(j_m-k_m)+2.5*(j_m-k_m))*10) ASC;
"""
#
# and saved in 2massc_jk_jt_hp5_forsf.txt. The basic set of counts with 
# 6 < J < 10, 0.0 < J-Ks < 0.8 in HEALPix pixels was generated by the following
# SQL query
#
"""
select floor(hp12index/16384), count(*) as count \
from twomass_psc, twomass_psc_hp12 \
where (twomass_psc.pts_key = twomass_psc_hp12.pts_key \
AND (ph_qual like 'A__' OR (rd_flg like '1__' OR rd_flg like '3__')) \
AND (ph_qual like '__A' OR (rd_flg like '__1' OR rd_flg like '__3')) \
AND use_src='1' AND ext_key is null \
AND (j_m-k_m) > 0.0 AND (j_m-k_m) < 0.8 AND j_m > 6 AND j_m < 10) \
group by floor(hp12index/16384) \
order by floor(hp12index/16384) ASC;
"""
#
# and saved in 2massc_hp5.txt
###############################################################################
import os, os.path
import numpy
import healpy
from matplotlib import cm
import gaia_tools.load
_BASE_NSIDE= 2**5
_BASE_NPIX= healpy.nside2npix(_BASE_NSIDE)
_SFFILES_DIR= os.path.dirname(os.path.realpath(__file__))
######################### Read file with counts in hp6 ########################
_2mc_skyonly= numpy.loadtxt(os.path.join(_SFFILES_DIR,'2massc_hp5.txt')).T
# Make sure all HEALPix pixels are available
ta= numpy.zeros((2,_BASE_NPIX))
ta[0][_2mc_skyonly[0].astype('int')]= _2mc_skyonly[0]
ta[1][_2mc_skyonly[0].astype('int')]= _2mc_skyonly[1]
_2mc_skyonly= ta
#################### Read file with counts in jt, j-k, hp5 ####################
_2mc= numpy.loadtxt(os.path.join(_SFFILES_DIR,'2massc_jk_jt_hp5_forsf.txt')).T
# Make value center of bin and re-normalize
_2mc[0]+= 0.5
_2mc[1]+= 0.5
_2mc[0]/= 10.
_2mc[1]= _2mc[1]*1.05/3.-0.05
class tgasSelect(object):
    def __init__(self,
                 min_nobs= 8.5,
                 max_nobs_std= 10.,
                 max_plxerr= 1.01, # Effectively turns this off
                 max_scd= 0.7,
                 min_comp= 0.,
                 min_lat= 20.):
        """
        NAME:
           __init__
        PURPOSE:
           Initialize the TGAS selection function
        INPUT:
        OUTPUT:
           TGAS-selection-function object
        HISTORY:
           2017-01-17 - Started - Bovy (UofT/CCA)
        """
        # Load the data
        self._full_tgas= gaia_tools.load.tgas()
        self._full_twomass= gaia_tools.load.twomass(dr='tgas')
        self._full_jk= self._full_twomass['j_mag']-self._full_twomass['k_mag']
        # Some overall statistics
        self._tgas_sid= (self._full_tgas['source_id']/2**(35.\
                               +2*(12.-numpy.log2(_BASE_NSIDE)))).astype('int')
        self._tgas_sid_skyonlyindx= (self._full_jk > 0.)\
            *(self._full_jk < 0.8)\
            *(self._full_twomass['j_mag'] > 6.)\
            *(self._full_twomass['j_mag'] < 10.)
        nstar, e= numpy.histogram(self._tgas_sid[self._tgas_sid_skyonlyindx],
                                  range=[-0.5,_BASE_NPIX-0.5],bins=_BASE_NPIX)
        self._nstar_tgas_skyonly= nstar
        return None

    def plot_mean_quantity_tgas(self,tag,
                                func=None,**kwargs):
        """
        NAME:
           plot_mean_quantity_tgas
        PURPOSE:
           Plot the mean of a quantity in the TGAS catalog on the sky
        INPUT:
           tag - tag in the TGAS data to plot
           func= if set, a function to apply to the quantity
           +healpy.mollview plotting kwargs
        OUTPUT:
           plot to output device
        HISTORY:
           2017-01-17 - Written - Bovy (UofT/CCA)
        """
        if func is None: func= lambda x: x
        mq, e= numpy.histogram(self._tgas_sid[self._tgas_sid_skyonlyindx],
                               range=[-0.5,_BASE_NPIX-0.5],bins=_BASE_NPIX,
                               weights=func(self._full_tgas[tag]\
                                                [self._tgas_sid_skyonlyindx]))
        mq/= self._nstar_tgas_skyonly
        cmap= cm.viridis
        cmap.set_under('w')
        kwargs['unit']= kwargs.get('unit',tag)
        kwargs['title']= kwargs.get('title',"")
        healpy.mollview(mq,nest=True,cmap=cmap,**kwargs)
        return None