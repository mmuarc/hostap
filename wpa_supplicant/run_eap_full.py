#!/usr/bin/python3
import subprocess
import signal
import os
import time
import sqlite3
import argparse
import atexit
import base64
import hashlib
import json
from datetime import datetime


# Constants


db_path_peer = "/tmp/noob_peer.db"

## DB funcs

def exec_query(query, db_path, args=[]):
    conn = sqlite3.connect(db_path)

    out = []
    c = conn.cursor()
    c.execute(query, args)
    conn.commit()
    # Should be changed if we want to handle all peers
    out = c.fetchone()
    conn.close()
    return out

def get_peers():
    """Retrieve PeerIds and SSIDs for peers that are ready for OOB transfer"""

    query = 'SELECT Ssid, PeerId from EphemeralState WHERE PeerState=1'
    data = exec_query(query, db_path_peer)
    return data
## OOB generation

def compute_noob_id(noob_b64):
    """Compute identifier for the OOB message"""

    noob_id = 'NoobId' + noob_b64
    noob_id = noob_id.encode('utf-8')
    noob_id = hashlib.sha256(noob_id).digest()
    noob_id_b64 = base64.urlsafe_b64encode(noob_id[0:16])
    noob_id_b64 = str(noob_id_b64, 'utf-8').strip('=')
    return noob_id_b64

def gen_noob():
    noob = os.urandom(16);
    noob_64 = base64.urlsafe_b64encode(noob);
    noob_64 = str(noob_64,'utf-8').strip('=');
    return noob_64

def compute_hoob(peer_id, noob):
    """Compute 16-byte fingerprint from all exchanged parameters"""

    query = 'SELECT MacInput FROM EphemeralState WHERE PeerId=?'

    data = exec_query(query, db_path_peer, [peer_id])
    if data is None:
        print('Query returned None in gen_noob')
        return None

    hoob_array = json.loads(data[0])
    hoob_array[len(hoob_array) - 1] = noob
    hoob_str = json.dumps(hoob_array, separators=(',', ':')).encode()
    hoob = hashlib.sha256(hoob_str).digest()
    hoob_b64 = base64.urlsafe_b64encode(hoob[0:16]).decode('ascii').strip('=')
    return hoob_b64


def generate_oob():
    peer = get_peers()
    noob = gen_noob()
    noob_id = compute_noob_id(noob)
    hoob = compute_hoob(peer[1], noob)
    sent_time = int(datetime.utcnow().timestamp())

    return {
        noob,
        noob_id,
        hoob,
        sent_time
    } 

def get_pid(arg):
    pid_list = []
    pname = arg.encode(encoding='UTF-8')
    p = runbash(b"ps -A | grep "+pname)
    if None == p:
        return None
    for line in p.splitlines():
        if pname in line:
            pid = int(line.split(None,1)[0])
            pid_list.append(pid)
    return pid_list

def runbash(cmd):
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE);
    out = p.stdout.read().strip();
    return out;

def kill_existing_supplicants():
    pid = get_pid('wpa_supplicant')
    for item in pid:
        os.kill(int(item),signal.SIGKILL)

def check_result():
    res = runbash("./wpa_cli status | grep 'EAP state=SUCCESS'")
    if res == b"EAP state=SUCCESS":
        return True
    return False

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--interface', dest='interface',help='Name of the wireless interface')
    args = parser.parse_args()

    kill_existing_supplicants()
   
    print("Starting wpa_supplicant...")
    cmd = "./wpa_supplicant -i "+args.interface+" -c wpa_supplicant.conf -Dnl80211 -d"
    wpa_process = subprocess.Popen(cmd,shell=True, stdout=1, stdin=None)

    while not check_result():
        time.sleep(5)
        oob = generate_oob()

def onExit():
    kill_existing_supplicants()

if __name__=='__main__':
    atexit.register(onExit)
    main()


