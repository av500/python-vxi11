import vxi11
import time
import sys

cnt = 0
pen = 0
xpos = 0
ypos = 0

def send_line(line):
	global cnt
	global pen
	if len(line) == 0 :
		return

	if line.find("PU") == 0:
		pen = 0;
	elif line.find("PD") == 0:
		pen = 1;
	
	print("SEND {} : {}".format(cnt, line))
	cnt += 1
	instr.write(line + '\r\n')

def handle_PA(prefix, line):
	global xpos, ypos
	send_line(prefix)

	if len(line) == 0 :
		return
	nums = line.split(",")
	nlen = len(nums)
	max_len = 16;
	if nlen > 0:
		pos = 0;
		while nlen > 0:
			line = "PA";
			loop = min(max_len, nlen)
			for x in range(loop) :
				#print(nums[pos])
				if ";" in nums[pos] :
					nums[pos] = nums[pos][:-1]
				line = line + nums[pos]
				coord = int(nums[pos])
				if (pos % 2) == 0 :
					xpos = coord
				else :
					ypos = coord
					print("x %d  y %d  pen %d" % (xpos, ypos, pen))

				if x < loop - 1 :
					line = line + ","
				elif ";" not in nums[pos] :
					line = line + ";"
				pos += 1				
			nlen -= max_len
			send_line(line)



instr = vxi11.Instrument("192.168.1.134", "gpib0,5", term_char = '\r')
print("plotter:  " + instr.ask("OI;"))
print("plotter:  " + hex(int(instr.ask("OS;"))))
print 'plotting:', str(sys.argv[1])

filepath = sys.argv[1]

with open(filepath) as fp:
	readline = fp.readline()
	readline = readline.strip();
	
	cnt = 1
	while readline:
		lines = readline.split(";")
		for line in lines:
			if line == "PD0,90":
				print("ignore: {}".format(line))
				continue
			if len(line) == 0 :
				continue
			if line[0] == '\n' or line[0] == '\r':
				continue
			line += ";"
			if line.find("PU") == 0:
				if line.find("PU;") == -1:
					# HP7225A does not understand PUx,y....
					handle_PA("PU;", line[2:])
				else : 
					send_line(line)
			elif line.find("PD") == 0:
				if line.find("PD;") == -1:
					# HP7225A does not understand PDx,y....
					handle_PA("PD;", line[2:])
				else :
					send_line(line)
			elif line.find("PA") == 0:
					# break long PA lines
					handle_PA("", line[2:])
			else :
				send_line(line)

		readline = fp.readline()
