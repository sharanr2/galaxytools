#!/usr/bin/env python
import argparse
import os
import shutil
import subprocess
import tempfile
import imagej2_base_utils

# Parse Command Line.
parser = argparse.ArgumentParser()
parser.add_argument( '--source_image', dest='source_image', help='Source image' )
parser.add_argument( '--source_image_format', dest='source_image_format', help='Source image format' )
parser.add_argument( '--target_image', dest='target_image', help='Target image' )
parser.add_argument( '--target_image_format', dest='target_image_format', help='Target image format' )
parser.add_argument( '--target_elastic_transformation', dest='target_elastic_transformation', default=None, help='Target elastic transformation matrix' )
parser.add_argument( '--source_raw_transformation', dest='source_raw_transformation', default=None, help='Source raw transformation matrix' )
parser.add_argument( '--max_heap_size_type', dest='max_heap_size_type', help='Type (default or megabytes) of max_heap_size value' )
parser.add_argument( '--max_heap_size', dest='max_heap_size', help='Maximum size of the memory allocation pool used by the JVM.' )
parser.add_argument( '--output', dest='output', help='Warping index' )

args = parser.parse_args()

tmp_dir = imagej2_base_utils.get_temp_dir()
source_image_path = imagej2_base_utils.get_input_image_path( tmp_dir, args.source_image, args.source_image_format )
target_image_path = imagej2_base_utils.get_input_image_path( tmp_dir, args.target_image, args.target_image_format )
target_elastic_transformation_path = imagej2_base_utils.get_input_image_path( tmp_dir, args.target_elastic_transformation, 'txt' )
source_raw_transformation_path = imagej2_base_utils.get_input_image_path( tmp_dir, args.source_raw_transformation, 'txt' )
# bUnwarpJ produces several lines of output that we need to discard, so
# we'll use a temporary output file from which we'll read only the last line.
tmp_output_path = imagej2_base_utils.get_input_image_path( tmp_dir, args.output, 'txt' )

# Set the size of the memory allocation pool used by the JVM.
memory_size = imagej2_base_utils.get_max_heap_size_value( args.max_heap_size_type, args.max_heap_size )

# Define command response buffers.
tmp_out = tempfile.NamedTemporaryFile().name
tmp_stdout = open( tmp_out, 'wb' )
tmp_err = tempfile.NamedTemporaryFile().name
tmp_stderr = open( tmp_err, 'wb' )

# Build the command line to align the two images.
cmd = imagej2_base_utils.get_base_cmd_bunwarpj( memory_size )
if cmd is None:
    imagej2_base_utils.stop_err( "bUnwarpJ not found!" )
cmd += ' -compare_elastic_raw'
cmd += ' %s' % target_image_path
cmd += ' %s' % source_image_path
cmd += ' %s' % target_elastic_transformation_path
cmd += ' %s' % source_raw_transformation_path
cmd += ' > %s' % tmp_output_path

# Calculate the warping index of elastic and raw transformations using bUnwarpJ.
proc = subprocess.Popen( args=cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=True )
rc = proc.wait()
if rc != 0:
    error_message = imagej2_base_utils.get_stderr_exception( tmp_err, tmp_stderr, tmp_stdout )
    imagej2_base_utils.stop_err( error_message )

# Example contents of tmp_output_path:
# ['Target image : ~/tmpHdt9Cs.jpg\n',
#  'Source image : ~/tmpu6kyfc.gif\n',
#  'Elastic Transformation file   : ~/tmp4vZurG.txt\n',
#  'Raw Transformation file : ~/tmp2PNQcT.txt\n',
#  ' Warping index = 25.007467512204983\n']
results = open( tmp_output_path, 'r' ).readlines()
warp_index = results[ -1 ].split( ' ' )[ -1 ]
outf = open( args.output, 'wb' )
outf.write( '%s' % warp_index )
outf.close()

imagej2_base_utils.cleanup_before_exit( tmp_dir )
