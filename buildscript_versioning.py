# This script is executed before each build (extra_scripts in platformio.ini). 

# It has 4 steps: 
# - It calculates a md5 hash of folders /src (version.h is deleted before) and /data
#   A six characters hash is then generated from the two folders hash concatenated.
#   The file version.h is then created with compile time, build number, build hash and version
# - Gets the chip id and mac address from the ESP (via serial connection only)
# - Generates the AP password from another ESP with the same pseudo random generation, based on chip id
# - Store all information in database 


Import("env")

import glob
import re
from serial.tools.list_ports import comports
import subprocess
import requests
import json

import datetime
import hashlib
import os
tm = datetime.datetime.today()

FILENAME_BUILDNO = 'versioning'
FILENAME_VERSION_H = 'include/version.h'
compileTime =  datetime.datetime.now()
version_root = 'v2.3.0.'
beta = ''
chip_id = ''
mac_address = ''
teleinfokitIdBase = "teleinfokit-"
# beta = ''


def create_device(payload):
    print(payload)
    headers = {'Content-Type': 'application/json'}

    try:
        response = requests.post("http://cassini:8780/devices", data=json.dumps(payload), headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Erreur lors de la requête de création. Code de statut: {response.status_code}")

    except requests.RequestException as e:
        raise Exception(f"Erreur lors de la requête HTTP: {e}")


# Fonction exécutée avant l'upload
def pre_upload_actions(source, target, env):
    print("=================================================================")
    print("===================== PRE UPLOAD ACTIONS ========================")

    try:
      print("Numero de série ? ")
      serialNum = input("=======> #E")

      if len(serialNum) != 0:            
        serialNum = "#E" + serialNum
        #  Lecture du Chip ID...
        chip_id = read_chipId()
        print("Obtention APKey...")
        APkey = getAPKey(chip_id)
        
        print("Sauvegarde device...")

        payload_tic = {
            "id": chip_id,
            "boardType": "teleinfokit",
            "name": teleinfokitIdBase + chip_id,
            "hwVersion": "4",
            "serialNumber": serialNum,
            "connectivityType": "wifi",
            "connectivity": {
              "macAddress": mac_address,
              "ipAddress": None,
              "dhcpFixed": False,
              "hostname": teleinfokitIdBase + chip_id + ".local",
              "wifiAP": {
                "ssid": "TeleInfoKit",
                "password": APkey,
                "authenticationMode": 1,
                "isHiddenSSID": False
              }
            },
            "firmware": {
              "name": "teleinfokit",
              "version": version,
              "repository": "https://github.com/342apps/teleinfokit",
              "firmwareUpdatePassword": APkey
            },
            "capabilities": None,
            "tagUrl": "https://342apps.net/module-teleinfokit/"
          }
        
        create_device(payload_tic)
      else:
         print("Pas d'upload sur Device MAnager")

      print(">>> PRE UPLOAD ACTIONS OK >>> RESET POUR UPLOAD")
      print("=================================================================")
    except Exception as e:
            print(f"Erreur : {e}")

# Fonction exécutée avant l'upload
def read_chipId():
    print("Lecture du Chip ID...")

    try:
        # print("Forcer le reset de l'ESP32...")
        # subprocess.run("esptool.py --chip esp8266 --port /dev/cu.usbserial* --before no_reset erase_flash")

        
        output = subprocess.check_output(
            f"esptool.py --chip esp8266 --port /dev/cu.usbserial* chip_id", 
            shell=True,
            text=True
        )

        mac_match = re.search(r"MAC:\s+([0-9a-fA-F:]+)", output)
        chip_id_match = re.search(r"Chip ID:\s+0x([0-9a-fA-F]+)", output)

        if mac_match and chip_id_match:
            global mac_address
            mac_address = mac_match.group(1)
            chip_id = chip_id_match.group(1)
            chip_id = chip_id.lstrip('0')
            
            print(f"========> MAC Address: {mac_address}")
            print(f"========> Chip ID: {chip_id}")
            return chip_id
        else:
            print("Impossible d'extraire les informations. Veuillez vérifier la sortie de la commande.")

    except subprocess.CalledProcessError as e:
            print(f"Erreur lors de l'exécution de la commande esptool.py : {e}")


def getAPKey(valeur_id):
    
    url = "http://192.168.0.111/key"
    params = {'id': valeur_id}

    print(f"Get APKey for chipID: {valeur_id}")

    try:
        response = requests.get(url, params=params)

        if response.status_code == 200:
            print(f"APKey = {response.text}")
            return response.text
        else:
            raise Exception(f"Erreur lors de la requête. Code de statut: {response.status_code}")

    except requests.RequestException as e:
        raise Exception(f"Erreur lors de la requête HTTP: {e}")


def cheaphash(string,length=6):
    if length<len(hashlib.sha256(string.encode('utf-8')).hexdigest()):
        return hashlib.sha256(string.encode('utf-8')).hexdigest()[:length]
    else:
        raise Exception("Length too long. Length of {y} when hash length is {x}.".format(x=str(len(hashlib.sha256(string).hexdigest())),y=length))

def GetHashofDirs(directory, verbose=0):
  import hashlib, os
  SHAhash = hashlib.md5()
  if not os.path.exists (directory):
    return -1

  try:
    for root, dirs, files in os.walk(directory):
      for names in files:
        if verbose == 1:
          print('Hashing', names)
        filepath = os.path.join(root,names)
        try:
          f1 = open(filepath, 'rb')
        except:
          # You can't open the file for some reason
          f1.close()
          continue

        while 1:
          # Read file in as little chunks
          buf = f1.read(4096)
          if not buf : break
          varhash = hashlib.md5(buf)
          SHAhash.update(varhash.hexdigest().encode('utf-8'))
        f1.close()

  except:
    import traceback
    # Print the stack traceback
    traceback.print_exc()
    return -2

  return SHAhash.hexdigest()

build_no = 0

if os.path.exists(FILENAME_VERSION_H):
  os.remove(FILENAME_VERSION_H)

hashsrc = GetHashofDirs('src', 1)
hashdata = GetHashofDirs('data', 1)
globalhash = cheaphash(hashsrc + hashdata)
version = version_root+str(globalhash)+beta
print("==> Hash of source files: "+globalhash)

with open(FILENAME_BUILDNO, 'w+') as f:
    f.write(str(globalhash))
    print('Build number: {}'.format(build_no))
    print('Build hash: {}'.format(globalhash))
    print('Version: {}'.format(version))

hf = """//  DO NOT EDIT MANUALLY THIS FILE - IT IS DELETED AND RECREATED AT EACH BUILD !!!! 
#ifndef BUILD_HASH
  #define BUILD_HASH "{}"
#endif
#ifndef VERSION
  #define VERSION "{}"
#endif
""".format(globalhash, version)
with open(FILENAME_VERSION_H, 'w+') as f:
    f.write(hf)


    
env.AddPreAction("upload", pre_upload_actions)
