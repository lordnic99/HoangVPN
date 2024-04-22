import os
import sys
import ctypes
import common
import wireguard_handler
import subprocess
import wg_generator
import shutil
import gsheet
import json
import win32serviceutil

CONFIG_VPN = ""

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False
    
def FIRST_INIT_CONFIG_AND_DIRECTORY():
    nssm_path = os.path.join("C:\\HoangVPN", "nssm.exe")
    
    try:
        win32serviceutil.QueryServiceStatus("HoangVPN")
    except:
        pass
    else:
        print("rathole exist removing")
        stop_command = [nssm_path, "stop", "HoangVPN"]
        subprocess.run(stop_command, check=True, creationflags=subprocess.CREATE_NO_WINDOW)
    
        remove_command = [nssm_path, "remove", "HoangVPN", "confirm"]
        subprocess.run(remove_command, check=True, creationflags=subprocess.CREATE_NO_WINDOW)
        
    main_path = r"C:\HoangVPN"
    if os.path.exists(main_path):
        shutil.rmtree(main_path)
    os.makedirs(main_path, exist_ok=True)
    
    shutil.copy("rathole.exe", main_path)   
    shutil.copy("nssm.exe", main_path)     
    shutil.copy("wiresock.msi", main_path)
    shutil.copy("wireguard.msi", main_path)
    shutil.copy("api.json", main_path)
    shutil.copy("redistx64.exe", main_path)
    shutil.copy("redistx86.exe", main_path)
                    
    os.chdir(main_path)
    
def ON_FINISH_INSTALLATION():
    os.remove("wiresock.msi")
    os.remove("wireguard.msi")
    os.remove("redistx64.exe")
    os.remove("redistx86.exe")
    os.remove("api.json")

def wireguard_start():
    wiresock_base = common.get_wiresock_installed_path()
    wiresock_bin = ""
    if wiresock_base != None:
        wiresock_bin = os.path.join(wiresock_base, r"wg-quick-config.exe")
        print(f"found wiresock bin: {wiresock_bin}")
    else:
        print("wiresock not found, reboot and try again")
        os._exit(1)
        
    command = wiresock_bin + r" --restart"
    try:
        env = os.environ.copy()
        env["PATH"] += os.pathsep + common.get_wireguard_installed_path()
        wiresock_p = subprocess.Popen(command, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=subprocess.CREATE_NO_WINDOW, env=env)
        wiresock_p.wait()
        if wiresock_p.returncode == 0:
            print("wiresock ok")
    except Exception as e:
        print("wiresock config failed restart and try agian")
        print(e)
        os._exit(1)
        
def wireguard_config_handler(udp_end_point):
    global CONFIG_VPN
    config_json_dest = r'C:\ProgramData\NT KERNEL\WireSock VPN Gateway\config.json'
    config_master_dest = r'C:\ProgramData\NT KERNEL\WireSock VPN Gateway\wiresock.conf'
    config_client_dest = r'C:\ProgramData\NT KERNEL\WireSock VPN Gateway\wsclient_1.conf'
    
    try:
        os.remove(config_json_dest)
        os.remove(config_master_dest)
        os.remove(config_client_dest)
    except OSError:
        pass
    
    server_private_key, server_public_key = wg_generator.generate_wireguard_keys()
    client_private_key, client_public_key = wg_generator.generate_wireguard_keys()
    
    server_config = wg_generator.create_server_config(server_private_key, client_public_key)
    client_config = wg_generator.create_client_config(client_private_key, server_public_key, udp_end_point)
    
    CONFIG_VPN = client_config
    
    with open(config_master_dest, "w") as server_file:
        server_file.write(server_config)
    with open(config_client_dest, "w") as client_file:
        client_file.write(client_config)
        
    json_config = wg_generator.fill_json_config(server_private_key=server_private_key,
                                                server_public_key=server_public_key,
                                                client_private_key=client_private_key,
                                                client_public_key=client_public_key,
                                                endpoint=udp_end_point)
    with open(config_json_dest, 'w') as file:
        json.dump(json_config, file, indent=4)
        
def rathole_client_generate(SERVER_IP, REMOTE_PORT, TUNNEL_TOKEN, DEVICE_ID):
    template = f'''[client]
remote_addr = "{SERVER_IP}:{REMOTE_PORT}"
default_token = "{TUNNEL_TOKEN}"

[client.services.{DEVICE_ID}]
type = "udp"
local_addr = "127.0.0.1:55555"
'''
    with open("client.toml", "w") as f:
        f.write(template)
    
def main():
    
    os.chdir(os.path.dirname(__file__))
    
    FIRST_INIT_CONFIG_AND_DIRECTORY()
    
    ################ GLOBAL VARIABLE #####################
    DEVICE_ID = common.generate_uuid()
    DEVICE_IP = common.get_public_ip()

    SERVER, SECRET_KEY, _ = gsheet.get_api_and_secret_key()
    if SERVER == None:
        with open("HOANGVPN.FAILED", "w") as f:
            pass
        ON_FINISH_INSTALLATION()

    REQUEST_TUNNEL_JSON = common.create_udp_tunnel(server=SERVER, secret_key=SECRET_KEY, device_id=DEVICE_ID)

    REMOTE_PORT = REQUEST_TUNNEL_JSON['remotePort']
    SERVER_IP = REQUEST_TUNNEL_JSON['serverIP']
    TUNNEL_TOKEN = REQUEST_TUNNEL_JSON['token']
    TUNNEL_ID = REQUEST_TUNNEL_JSON['tunnelID']
    BIND_PORT = REQUEST_TUNNEL_JSON['bindPort']
    
    
    print("prepare wireguard and wiresock")
    wireguard_handler.main()
    
    print("request create tunnel")
    rathole_client_generate(SERVER_IP, 
                            REMOTE_PORT, 
                            TUNNEL_TOKEN, 
                            DEVICE_ID)
    
    common.rathole_service_install()
    
    
    
    print("prepare config for wireguard")
    wireguard_config_handler(f"{SERVER_IP}:{BIND_PORT}")
    
    print("wireguard start")
    wireguard_start()

    gsheet.push_data_to_gsheet(UUID=DEVICE_ID, 
                                  TOKEN_REGISTER=TUNNEL_TOKEN, 
                                  TUNNEL_ID=TUNNEL_ID, 
                                  PUBLIC_IP=DEVICE_IP,
                                  VPN_CONFIG=CONFIG_VPN,
                                  API_KEY=SECRET_KEY)
    
    with open("HOANGVPN.INSTALLED", "w") as f:
        pass
    
    ON_FINISH_INSTALLATION()
    
if is_admin():
    main()
else:
    ctypes.windll.shell32.ShellExecuteW(None,  "runas", sys.executable, " ".join(sys.argv), None, 1)
    