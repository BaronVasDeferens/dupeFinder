
# DupeFinder
# Author: Skot West 2016
# Scans and catalogs files within a directory tree and compiles a list of all duplicate files.


# TODO: handle links sensibly
# TODO: allow for customizable output
# TODO: add Windows support

from sys import argv
import os
import subprocess

directoriesToSearch = []
namesAndHashes = {}
completedDirs = []
duplicates = []
recursiveDepth = 99999
fileFilter = ""
verbosity = False


# ProcessDir accepts a directory name argument and a depth argument.
# Where depth < 0, the directory is not examined.
# This function first examines the log of already completed directories; if the dir hasn't already been 
# processed, then its contents will be examined. 
# Each (non-directory) file will be hashed and both the name (plus its absolute path) and the hash will be added
# to a global "namesAndHashes" dictionary. Sub-directories are added to a list for later processing.

def processDir(dir, depth):

	global namesAndHashes
	global fileFilter
	global verbosity
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

	print("Scanning " + dir + ": " + str(len(os.listdir(dir))) + " files...")

	# BEGIN CATALOGING
	# namesAndHashes will store the key/item pairs as follows (hash : absolute path + file name)  

	# For each object in this directory, deteremine if it is a file or a directory;
	# For each file, generate a sha1 hash; for each directory, add it to the "dirQueue"

	for i in os.listdir(dir):
		fileName = i
		
		# convert i into an absolute path
		i = dir + "/" + i

		if os.path.isfile(i):

			# File filter check:
			# examine the last n characters of fileName and compare them to fileFilter
			if (fileFilter == "") or (fileName[-len(fileFilter):] == fileFilter):
						
				# Create subprocess to run the SHA1 hash on the file
				retVal = subprocess.check_output(['sha1sum', '-b', i])
				retVal = retVal[0:40]

				if verbosity:
					print("\t" + fileName + ": " + retVal)

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

def printUsage():
	print("USAGE:")
	print("\t python dupeFinder [flags] dir_to_search [addl_dirs_to_search]")
	print("FLAGS:")
	print("\t -r recursive_depth: controls depth of search.")
	print("\t -f file_type: match only specific file types (e.g. .mp3)")
	print("\t -v: displays everything, including SHA1 values")
	print("\n")
	return


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

# FLAG: VERBOSE DISPLAY
# -v


# Examine content of argv
# No arguments or directories found: throw an error
if len(argv) <= 1:
	print(">>> ERROR: please specify a directory you wish to scan for duplicates.")
	exit()
else:
	# Find flags and directives
	# We are interested in positions 1,2,3,4...through n, where n is the number of total possible flag/argument pairs
	# The case with the fewest possible arguments is: "dupeFinder.py /"
	#pos  0       1 2  3   4 	5
	# dupeFinder -r 3 -f .mp3 ~/Music
	
	for i in range(1,len(argv)):
		
		# Recursive depth
		if argv[i] == ("-r"):
			try:
				if argv[i+1].isdigit():
					recursiveDepth = int(argv[i+1])
					i = i + 1
				else:
					print("ERROR: -r flag requires numeric argument. See USAGE")
					exit()
			except:
				printUsage()
				exit()

		# File types
		elif argv[i] == ("-f"):
			try:
				if argv[i+1].startswith(".") and len(argv[i+1]) > 1:
					fileFilter = argv[i+1]
					i = i + 1
				else:
					print("ERROR: -f flag requires filetype argument (a period followed by at least one character). See USAGE")
					exit()
			except:
				printUsage()
				exit()

		# Verbose display flag
		elif argv[i] == ("-v"):
			verbosity = True

		# Directory argument
		elif os.path.isdir(argv[i]):
			directoriesToSearch.append(argv[i])


# Check: did the user provide ANY directories to search?
if len(directoriesToSearch) <= 0:
	printUsage()
	exit()


# DEBUG: display all parameters
print("PARAMETERS:")
print("\tRecursive depth: " + str(recursiveDepth))
print("\tFile filter: " + fileFilter)
print("\tVerbosity: " + str(verbosity))
print("\n")


for dir in directoriesToSearch:
	if os.path.isdir(dir):
		processDir(os.path.abspath(dir), recursiveDepth)


print("\n*** FINISHED! ***\n")
print(str(len(namesAndHashes)) + " total files scanned.")
print(str(len(duplicates)) + " duplicates found: ")
for dupe in duplicates:
	print(dupe)
