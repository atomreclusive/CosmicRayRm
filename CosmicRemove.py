import numpy as np
import time
import sys
from PIL import Image
from scipy.interpolate import RectBivariateSpline
from scipy.signal import convolve2d, medfilt2d
#from scipy.ndimage import median_filter
from skimage.measure import block_reduce

''' Cosmic Ray Removal Algorithm as described by
"Cosmic-Ray Rejection by Laplacian Edge Detection"
Pieter G. van Dokkum
Astronomical Society of the Pacific, 113:1420–1427, 2001

https://doi.org/10.1086/323894

Variable names attempt to correspond to those in the above article
'''


class cr_det:
    # Define detector characteristics
    def __init__(self, img, read_noise=12.38, gain=1.00, subsamp_fac=2):

        if not isinstance(subsamp_fac, int):
            print("subsamp_fac not type int. Please change to int")
            sys.exit()


        #self.I = np.asarray(Image.open(img),dtype=np.uint8)
        self.I = np.asarray(Image.open(img))
        self.read_noise = read_noise  # rms in electrons
        self.gain = gain  # e-/ADU
        self.subsamp_fac = subsamp_fac

        img_size = np.shape(self.I)

        self.cr_loc = []

    def rm_bkgd(self, bkgd):
        B = np.asarray(Image.open(bkgd),dtype=float)
        #self.I = np.asarray(self.I.astype(float) - B).astype(np.uint8)
        self.I = self.I - B

    def find(self, LF_thresh=2, S_thresh=5, mode='both'):
        gain = self.gain
        read_noise = self.read_noise
        ssf = self.subsamp_fac
        img_size = np.shape(self.I)

        # interpolate using step function, i.e. set kx,ky = 0
        I2 = RectBivariateSpline(
                x=range(0, ssf*img_size[0], ssf),
                y=range(0, ssf*img_size[1], ssf),
                z=self.I,
                kx=1, ky=1
                )

        # make correct size
        I2 = I2(
                range(ssf*img_size[0]),
                range(ssf*img_size[1])
                )

        # kernel = del^2 * f, used to calculate Laplacian image L
        kernel = np.array([
                [0, -0.25, 0],
                [-0.25, 1, -0.25],
                [0, -0.25, 0]
            ])
        
        L2 = convolve2d(I2, kernel, mode='same')

        L2_p = np.copy(L2)
        L2_p[L2 < 0] = np.int32(0)
        L_p = np.empty(img_size, dtype=np.int32)

        L_p = block_reduce(L2_p, block_size=(ssf,ssf), func=np.mean)


        # Noise model
        N = np.sqrt( gain*(medfilt2d(self.I, kernel_size=5)) + read_noise**2 )/gain
        #N = np.sqrt( gain*(median_filter(self.I, size=5)) + read_noise**2 )/gain

        S = L_p/(ssf*N)
        #S = L_p/N
        S_naught = S - medfilt2d(S, kernel_size=5)
        #S_naught = S - median_filter(S, size=5)

        F = medfilt2d(self.I, kernel_size=3) - medfilt2d( medfilt2d(self.I, kernel_size=3), kernel_size=7 ) 
        #F = median_filter(self.I, size=3) - median_filter( median_filter(self.I, size=3), size=7 ) # filter for fine structures; mostly for astro

        LF = np.zeros(L_p.shape) 
        np.divide(L_p,F, out=LF, where= F != 0) 
        # ^^^ looking for contrast between Laplacian filter and fine structure filter; tries to distinguish b/w cosmic rays and actual structure

        if mode == 'LF':
            cr_row, cr_col = np.nonzero( LF>LF_thresh )
        elif mode == 'S':
            cr_row, cr_col = np.nonzero( S>S_thresh )
        elif mode == 'both':
            cr_row, cr_col = np.nonzero( np.bitwise_and( S>S_thresh, LF>LF_thresh ) )

        edges = np.bitwise_or(
            np.bitwise_or(cr_row == 0,cr_row ==(img_size[0]-1)), 
            np.bitwise_or(cr_col == 0,cr_col ==(img_size[1]-1))
            )

        cr_row = np.delete(cr_row, np.where(edges))
        cr_col = np.delete(cr_col, np.where(edges))

        self.cr_loc = np.transpose( (cr_row, cr_col) )
        self.S = S
        self.F = F
        self.LF = LF
        return self.cr_loc

    def rm(self):
        for loc in self.cr_loc:
            self.I[ loc[0], loc[1] ] = np.nan
            self.I[ loc[0], loc[1] ] = np.nanmedian( self.I[ loc[0]-2:loc[0]+3 , loc[1]-2:loc[1]+3 ] )
