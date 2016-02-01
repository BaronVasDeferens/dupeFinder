from sys import argv

if len(argv) > 2:
	if (argv[1] == ("-r")) and argv[2].isdigit():
		print("recursiveDepth is " + argv[2])

for i in range(0,len(argv)):
	print(str(i) + ": " + argv[i])
