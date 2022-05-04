#!/usr/bin/python3

from CosmicRemove import cr_det 
import matplotlib.pyplot as plt
import sys
import os
import argparse

# Construct an argument parser
cr_args = argparse.ArgumentParser(description='A tool for finding and removing cosmic rays.')

# Add arguments to the parser
cr_args.add_argument("-img", "--image", required=True, type=str,
    help="Image to process")
cr_args.add_argument("-bg", "--background", default=None, type=str,
    help="Background image to subtract")
cr_args.add_argument("-S", "--S_lim", default=5, type=float,
    help="Noise scaled threshold")
cr_args.add_argument("-LF", "--LF_lim", default=2, type=float,
    help="Fine Structure scaled threshold")
args = vars(cr_args.parse_args())

img_name = args['image'].split('.')[0]
mode = 'both'
newdir = img_name + "_" + mode

if not os.path.isdir(newdir):
    os.mkdir(newdir)

i = cr_det(args['image'])

if args['background'] != None:
    i.rm_bkgd(args['background'])

plt.figure(figsize=(16,24))
fig, (ax1, ax2) = plt.subplots(1,2)
fig.set_tight_layout(True)
im1 = ax1.imshow(i.I, interpolation='none', resample=False)
plt.colorbar(im1, ax=ax1, orientation='horizontal')
ax1.set_xticks([])
ax1.set_yticks([])
ax1.set_title("Before")

count = 0
while True:
    i.find(S_thresh=0.75, LF_thresh=1, mode='both')
    if i.cr_loc.any():
        count+=1
        i.rm()
        if mode=='both' or mode=='S':
            f = plt.figure(figsize=(8,6))
            plt.tight_layout()
            plt.imshow(i.S, interpolation='none', resample=False)
            plt.colorbar()
            plt.xticks([])
            plt.yticks([])
            plt.title('S'+str(count))
            plt.savefig(os.path.join(newdir, img_name + '_S' + str(count) + '.png'), dpi=300)
            plt.close(f)

        if mode=='both' or mode=='LF':
            f = plt.figure(figsize=(8,6))
            plt.tight_layout()
            plt.imshow(i.LF, interpolation='none', resample=False)
            plt.colorbar()
            plt.xticks([])
            plt.yticks([])
            plt.title('LF'+str(count))
            plt.savefig(os.path.join(newdir, img_name + '_LF' + str(count) + '.png'), dpi=300)
            plt.close(f)
    else:
        break 

im2 = ax2.imshow(i.I, interpolation='none', resample=False)
plt.colorbar(im2, ax=ax2, orientation='horizontal')
ax2.set_xticks([])
ax2.set_yticks([])
ax2.set_title("After")
fig.savefig(os.path.join(newdir, img_name + '_BeforeAfter.png'), dpi=300)
