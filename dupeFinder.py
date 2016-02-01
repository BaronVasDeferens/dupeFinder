
# DupeFinder
# Author: Skot West 2016
# Scans and catalogs files within a directory tree and compiles a list of all duplicate files.


# TODO: handle links sensibly
# TODO: specify filetype filter


# Usage: 

from sys import argv
import os
import subprocess

directoriesToSearch = []
namesAndHashes = {}
completedDirs = []
duplicates = []
recursiveDepth = 99999
fileFilter = ""


# ProcessDir accepts a directory name argument and a depth argument.
# Where depth < 0, the directory is not examined.
# This function first examines the log of already completed directories; if the dir hasn't already been 
# processed, then its contents will be examined. 
# Each (non-directory) file will be hashed and both the name (plus its absolute path) and the hash will be added
# to a global "namesAndHashes" dictionary. Sub-directories are added to a list for later processing.

def processDir(dir, depth):

	global namesAndHashes
	global completedDirs
	global duplicates

	# "dirQueue" is a list of the current directory's sub-directories
	dirQueue = []

	# Check for recursive depth: do not proceed if less than zero
	if depth < 0:
		return

	# check whether this directory has already been scanned
	if dir in completedDirs:
		print(">>> Already processed " + dir + ". Skipping...")
		return

	print("Scanning " + dir + "...")

	print(str(len(os.listdir(dir))) + " files found...\n")

	# BEGIN CATALOGING
	# namesAndHashes will store the key/item pairs as follows (hash : absolute path + file name)  

	# For each object in this directory, deteremine if it is a file or a directory;
	# For each file, generate a sha1 hash; for each directory, add it to the "dirQueue"

	for i in os.listdir(dir):
		i = dir + "/" + i

		if os.path.isfile(i):
			retVal = subprocess.check_output(['sha1sum', '-b', i])
			retVal = retVal[0:40]

			# Test whether namesAndHashes already contains an identical for this file hash;
			# If a duplicate is found, add the name to the list, "duplicates"
			# Otherwise, add it to namesAndHashes
			if retVal in namesAndHashes:
				duplicates.append((i,namesAndHashes[retVal]))
			else:
				namesAndHashes[retVal] = i

		elif os.path.isdir(i):
			dirQueue.append(i)

	# Having completed, append this directory to the list of completed directories. 
	completedDirs.append(os.path.abspath(dir))
	
	# Finally, process all the sub-directories.
	for i in dirQueue:
		processDir(os.path.abspath(i), (depth-1) )

	return
#end processDir



# EXECUTION BEGINS HERE

# FLAGS AND DIRECTIVES
# All flags and directives must immediate follow the call to DupeFinder (e.g. "DupeFinder -r 1 -f .mp3 ~/Music")
# Flags can be listed in any order so long as they immediately follow the call to DupeFinder

# FLAG: DEPTH CONTROL FOR RECURSIVE SEARCH
# -r number_of_levels
# By default, DupeFinder will perform and exhaustive recursive search on any/all folders listed.
# With the "recurse" flag, the user may specify the recursive depth.

# FLAG: FILTER BY FILE TYPE
# -f file_type

# FLAG: DISPLAY SHA1 HASH RESULTS


# Examine content of argv
if len(argv) > 1:

	# Find flags and directives
	# We are interested in positions 1,2,3,4
	
	#pos  0       1 2  3   4 	5
	# dupeFinder -r 3 -f .mp3 ~/Music
	
	# Look for recursive depth control flag
	# TODO: as more flags and options are added, we'll need to search through argv a little more sensibly
	if (len(argv) > 2):		
		if (argv[1] == ("-r")) and argv[2].isdigit():
			recursiveDepth = int(argv[2])
		if (argv[1] == ("-f")) and argv[2].startswith("."):
			fileFilter = argv[2]

	for i in range(1,len(argv)):
		directoriesToSearch.append(argv[i])

# No arguments or directories found: throw an error
else:
	print(">>> ERROR: please specify a directory you wish to scan for duplicates.")
	exit()




for dir in directoriesToSearch:
	if os.path.isdir(dir):
		processDir(os.path.abspath(dir), recursiveDepth)


print("FINISHED!\n")
print(str(len(namesAndHashes)) + " total files scanned.")
print(str(len(duplicates)) + " duplicates found: ")
for dupe in duplicates:
	print(dupe)
