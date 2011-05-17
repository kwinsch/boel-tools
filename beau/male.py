import belib.crypt.hash as beHash
import httplib2
import mimetypes


http = httplib2.Http()
file = "beerb_design.pdf"
data = open(file, "rb").read()
mime = mimetypes.guess_type(file)[0]
hash = beHash.getFileSha1(file)
url = "http://23.couchone.com:5984/befiles/" + hash + "/blob"
headers = {"Content-type": mime}

print(mime + "  " + hash)

resp, content = http.request(url, "PUT", body=data , headers=headers)
