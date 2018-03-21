import sys
import operator
from functools import cmp_to_key

def _compare(x,y):
	i,j = 0,0
	while i < len(x) and j < len(y):
		if x[i].isdigit() and y[i].isdigit():
			s1,s2 = "",""
			while i < len(x) and x[i].isdigit():
				s1 += x[i]
				i+=1
			while j < len(y) and y[j].isdigit():
				s2 += y[j]
				j+=1
			if int(s1) > int(s2):
				return 1
			elif int(s1) < int(s2):
				return -1
		else:
			#忽略大小写
			a,b = x[i].lower(),y[i].lower()
			if operator.gt(a,b):
				return 1
			elif operator.lt(a,b):
				return -1
			else:
				i+=1
				j+=1
	return 0

def Sort(src):
	if isinstance(src,list):
		return sorted(list_str,key = cmp_to_key(_compare))
	else:
		out_filename = "sorted" + src
		infile = open(src)
		outfile = open(out_filename,"w")
		try:
			list_lines = infile.read().splitlines()
			while '' in list_lines:
				list_lines.remove('')
			list_lines.sort(key=cmp_to_key(__compare))
			result = map(lambda x:x + '\n',list_lines)
			outfile.writelines(result)
			return list_lines
		except Exception as e:
			raise e
		finally:
			infile.close()
			outfile.close()

def main():
	if len(sys.argv) != 2:
		raise Exception("只能传入被排序的文件路径")
	else:
		start(sys.argv[1])

if __name__ == "__main__":
	main()