
# DupeFinder
# Scans and catalogs files within a directory tree and revealing all duplicate files.

from sys import argv
import os
import subprocess

directoriesToSearch = []
namesAndHashes = {}
completedDirs = []
duplicates = []

# ProcessDir first examines the log of completed directories. If the dir hasn't been processed,
# then the contents will be examined. Files will have sha1 added to the list and directories will
# be added to a queue to be processed later.

def processDir(dir):

	global namesAndHashes
	global completedDirs
	global duplicates

	print("Scanning " + dir + "...")

	# dirQueue is a list of sub-directories to be examined next
	dirQueue = []

	# check whether this directory has already been scanned
	if dir in completedDirs:
		print(">>> Already processed " + dir + ". Skipping...")
		return

	# BEGIN CATALOGING
	# namesAndHashes will store the key/item pairs as follows (hash : file name)  

	# for each listing in this directory, deteremine if it is a file or a directory;
	# generate a sha1 hash for each file and store

	print(str(len(os.listdir(dir))) + " files found...\n")

	for i in os.listdir(dir):
		i = dir + "/" + i

		if os.path.isfile(i):
			retVal = subprocess.check_output(['sha1sum', '-b', i])
			retVal = retVal[0:40]

			# test whether the namesAndHashes already contains the same hash:
			if retVal in namesAndHashes:
				duplicates.append((i,namesAndHashes[retVal]))
				# duplicates.append((str(dir + "/" + i),namesAndHashes[retVal]))
			else:
				namesAndHashes[retVal] = i
				# namesAndHashes[retVal] = str(dir + "/" + i)

		elif os.path.isdir(i):
			dirQueue.append(i)

	# Having completed, append this directory to the liost of completed directories. 
	completedDirs.append(os.path.abspath(dir))
	
	# Finally, process all the sub-directories.
	for i in dirQueue:
		#processDir(i)
		processDir(os.path.abspath(i))

	return
#end processDir



# EXECUTION BEGINS HERE

# check for presence of at least one argument
if len(argv) > 1:
	for i in range(1,len(argv)):
		directoriesToSearch.append(argv[i])
else:
	print(">>> ERROR: please specify a directory you wish to scan for duplicates.")
	exit()

# check whether the specified directory is actually a directory
#if os.path.isdir(baseDir) == False:
#	print(">>> ERROR: " + baseDir + " is not a valid directory.")
#	exit()

for dir in directoriesToSearch:
	if os.path.isdir(dir):
		#processDir(dir)
		processDir(os.path.abspath(dir))


print("\n")
print(str(len(namesAndHashes)) + " total files scanned!")
print(str(len(duplicates)) + " duplicates found: ")
for dupe in duplicates:
	print(dupe)
