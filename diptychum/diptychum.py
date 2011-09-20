import os.path as op
import shutil, subprocess
import urllib.request, urllib.parse
import json
#import argparse

#parser = argparse.ArgumentParser(description='diptychum label generator')

#parser.add_argument('action',
#    choices = ['new', 'update'],
#    help = 'Update images on labels or create new ones')
#parser.add_argument('action',
#    choices = ['vinum-1l', 'spiritus-1l'],
#    help = 'label template')
#parser.add_argument('-n', '--number',
#   required = False,
#    default = 1,
#    help = 'How many labels?')

#args = parser.parse_args()

# Argparse introduced in python 3.2
num = 15
ltype = 'vinum-1l'
alcv = "6"
myear = "2011"
plant_l1 = 'Rheum'
plant_l2 = 'Rhabarbarum L.'

def label_spiritus():
	exit()

# Spiritus has no QR Code
if ltype == 'spiritus-1l':
	label_spiritus1l()

url = 'http://192.168.1.49:8023/numericus/url/' + str(num)
req = urllib.request.Request(url)
res_data = urllib.request.urlopen(req)

jdata = json.loads(res_data.read().decode('utf-8'))
urldata = jdata['boelURL']
gchart = 'http://chart.apis.google.com/chart?cht=qr&chs=350x350&chl='

# Download QRcodes from Google charts
for beurl in urldata:
	urlstr = urllib.parse.quote(urldata[beurl],safe='')
	o_file = 'tmp/' + beurl + '_qr.png'
	r_url = gchart + urlstr
	r_req = urllib.request.Request(r_url)
	f = urllib.request.urlopen(r_req)
	print("downloading ", r_url)
	# Open our local file for writing
	local_file = open(o_file, "wb")
	#Write to our local file
	local_file.write(f.read())
	local_file.close()

# Spiritus has no QR Code
if ltype == 'vinum-1l':
	output_file = 'vinum-1l.tex'
	header_fp = open('tex/vinum-1l_header.inc', 'r')
	footer_fp = open('tex/vinum-1l_footer.inc', 'r')
	fp = open(output_file, 'w')
	fp.write(header_fp.read())
	header_fp.close()

	for beurl in urldata:
		fp.write('\\begin{picture}(62,100)(3,0)\n')
		fp.write('\\put(0,0){\\background}\n')
		fp.write('\\put(5,80){\\Huge '+plant_l1+'}\n')
		fp.write('\\put(5,73){\\Huge '+plant_l2+'}\n')
		fp.write('\\put(0,0){\\includegraphics[width=18mm]{./tmp/'+beurl+'_qr.png}}%\n')
		fp.write('\\put(50,6){\\small '+alcv+' \\% Vol.}\n')
		fp.write('\\put(50,3){\\small '+myear+'}\n')
		fp.write('\\end{picture}\n')
		if num > 1:
			fp.write('\n\n\\newpage\n')
		
	fp.write(footer_fp.read())
	footer_fp.close()
	fp.close()
	
	retcode = subprocess.call(["pdflatex", output_file])
