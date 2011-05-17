# Copyright (c) 2011, Kevin Bortis
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#    1. Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#    2. Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#    3. Neither the names of the copyright holders nor the names of any
#       contributors may be used to endorse or promote products derived
#       from this software without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

import os, shutil, sys
import configparser, argparse, json
import belib.crypt.hash as beHash
import belib.contrib.crypt.gnupg as gnupg

# Project root
beroot = '.be'

# Get User information. First parse ~/.gitconfig and
# overwrite data with values from ~/.beconfig and
# then .be/config if availlable.
config = configparser.RawConfigParser()
config.read([os.path.expanduser('~/.gitconfig'),
  os.path.expanduser('~/.beconfig'),
  beroot+'/config'])
bename = config.get('user', 'name')
beemail= config.get('user', 'email')

# Parsing command line arguments
parser = argparse.ArgumentParser(
    description = 'Project data management')
parser.add_argument('action',
    choices = ['init', 'add', 'commit', 'push', 'reset'],
    help = 'help string for action')
parser.add_argument('targets',
    metavar = 'FILES',
    nargs = '+',
    help = 'Files to process')
parser.add_argument('-u', '--user',
    required = False,
    default = beemail,
    help = 'GPG sign mail adress')
parser.add_argument('-m', '--message',
                    required = False,
                    help = 'Commit message')

args = parser.parse_args()

# Test if in Project root dir, if not abbort
if not(os.path.exists(".be")):
  if not args.action == 'init':
    sys.exit("Please cd to the project root")

print(os.getcwd())

# Initialising a new project
if args.action == 'init':
  if args.targets[0] == '.':
    beprojdir = os.getcwd()
    if not(os.path.exists('.be')):
      os.makedirs('.be/commits')
      os.mkdir('.be/blobs')
      os.mkdir('.be/tree')
      print("Project creation complete")
    else:
      print("Project folder already initialized")
  else:
    beprojdir = args.targets[0]
    if not(os.path.exists(beprojdir)):
      os.mkdir(beprojdir)
      os.mkdir(beprojdir+'/.be')
      os.mkdir(beprojdir+'/.be/blobs')
      print("Project creation complete")
    else:
      print("Project folder already exists")
      print("Project creation abborted")

# Adding files to project
if args.action == 'add':
  # commit container
  commit_hashs = []
  commit = {}
  commit.update(trees=commit_hashs)
  if (os.path.exists(beroot+'/NEXT')):
    f=open(beroot+'/NEXT', 'r')
    commit = json.loads(f.read())
    f.close()
  else:
    commit.update(father="ORIGO")
  # Processing files
  commit_hashs = commit.get('trees', [])
  for target in args.targets:
    # Create blob
    thash = beHash.getFileSha1(target)
    tpre = thash[0:2]
    tpost = thash[2:]
    if not(os.path.exists(beroot+'/blobs/'+tpre)):
      os.mkdir(beroot+'/blobs/'+tpre)
    shutil.copy(target, beroot+'/blobs/'+tpre+'/'+tpost)
    # Create tree object for file
    treeobj = {}
    treeobj.update(filename=os.path.basename(target))
    treeobj.update(blobhash=thash)
    treestr = json.dumps(treeobj)
    treehash = beHash.getSha1(treestr.encode('utf-8'))
    treepre = treehash[0:2]
    treepost = treehash[2:]
    if not(os.path.exists(beroot+'/tree/'+treepre)):
      os.mkdir(beroot+'/tree/'+treepre)
    if not(os.path.exists(beroot+'/tree/'+treepre+'/'+treepost)):
      f = open(beroot+'/tree/'+treepre+'/'+treepost, 'w')
      f.write(treestr)
      f.close()
      # Add file to commit
      commit_hashs.append(treehash)
  # Write commit list
  commit_hashs = list(set(commit_hashs))
  commit.update(trees=commit_hashs)
  commit_str = json.dumps(commit)
  f = open(beroot+'/NEXT', 'w')
  f.write(commit_str)
  f.close()

# Adding files to project
if args.action == 'commit':
  # Import and verify NEXT
  f=open(beroot+'/NEXT', 'r')
  commit = json.loads(f.read())
  f.close()
  # Check if commit makes sense
  if not 'trees' in commit:
    sys.exit("Nothing to commit...")
  # Get commit message from user or -m parameter
  if (args.message == None):
    cmsg = input("Please enter a commit message: ")
    print(cmsg)
  else:
    cmsg = args.message
  commit.update(message=cmsg)
  # Write commit file
  commit_str = json.dumps(commit)
  commit_hash = beHash.getSha1(commit_str.encode('utf-8'))
  commit_pre = commit_hash[0:2]
  commit_post = commit_hash[2:]
  if not(os.path.exists(beroot+'/commits/'+commit_pre)):
      os.mkdir(beroot+'/commits/'+commit_pre)
  f = open(beroot+'/commits/'+commit_pre+'/'+commit_post, 'w')
  f.write(commit_str)
  f.flush()
  os.fsync(f.fileno())
  f.close()
  # Sign commit file
  gpg = gnupg.GPG(verbose=False)
  # (self, gpgbinary='gpg', gnupghome=None, verbose=False)
  f = open(beroot+'/commits/'+commit_pre+'/'+commit_post, 'rb')
  signed_data = gpg.sign_file(f, keyid="6F8BF0D2", detach=True)
  sigFile = open(beroot+'/commits/'+commit_pre+'/'+commit_post+'.sig', 'w+b')
  # b means binary mode. Needed on Windows, doesn't hurt on UNIX
  sigFile.write(signed_data.data)
  sigFile.close()
  f.close()
  # Create new NEXT with correct father
  f = open(beroot+'/NEXT', 'w')
  commit = {}
  commit.update(father=commit_hash)
  commit_str = json.dumps(commit)
  f.write(commit_str)
  f.close()

# Adding files to project
if args.action == 'push':
  print("pushing files to server. Not implemented")

# Adding files to project
if args.action == 'reset':
  print("Remove files from current working commit")
