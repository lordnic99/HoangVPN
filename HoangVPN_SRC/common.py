import uuid
import requests
import os
import subprocess
import winreg
import win32com.client

os.chdir(os.path.dirname(__file__))

def generate_uuid():
    new_uuid = str(uuid.uuid4().hex).upper()
    new_uuid = new_uuid[:10]
    return new_uuid
    
def create_udp_tunnel(server, secret_key, device_id):
    url = f"http://{server}/createtunnel"
    headers = {
        "Authorization": f"{secret_key}",
        "Content-Type": "application/json"
    }
    data = {
        "name": f"{device_id}"
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 201:
            return response.json()
    except requests.exceptions.RequestException as e:
        print(response.json())
        return None
    
def rathole_service_install():
    nssm_path = os.path.join("C:\\HoangVPN", "nssm.exe")
        
    install_command = [nssm_path, "install", "HoangVPN", r"C:\HoangVPN\rathole.exe", "client.toml"]
    subprocess.run(install_command, check=False, creationflags=subprocess.CREATE_NO_WINDOW)
    
    set_autostart_command = [nssm_path, "set", "HoangVPN", "Start", "SERVICE_AUTO_START"]
    subprocess.run(set_autostart_command, check=False, creationflags=subprocess.CREATE_NO_WINDOW)
    
    start_service_command = [nssm_path, "start", "HoangVPN"]
    subprocess.run(start_service_command, check=False, creationflags=subprocess.CREATE_NO_WINDOW)
    return
        
def get_wiresock_installed_path():
    root_key = winreg.HKEY_LOCAL_MACHINE
    subkey = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Installer\Folders"
    try:
        key = winreg.OpenKey(root_key, subkey)
        for i in range(winreg.QueryInfoKey(key)[1]):
            value_name = winreg.EnumValue(key, i)[0]
            if "WireSock" in value_name:
                if "bin" in value_name:
                    return value_name
    except FileNotFoundError:
        pass
    except Exception as e:
        return None
    finally:
        key.Close()    
        
def get_wireguard_installed_path():
    root_key = winreg.HKEY_LOCAL_MACHINE
    subkey = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Installer\Folders"
    try:
        key = winreg.OpenKey(root_key, subkey)
        for i in range(winreg.QueryInfoKey(key)[1]):
            value_name = winreg.EnumValue(key, i)[0]
            if "WireGuard" in value_name:
                return value_name
    except FileNotFoundError:
        pass
    except Exception as e:
        return None
    finally:
        key.Close()    
        
def get_public_ip():
    try:
        response = requests.get("https://api.ipify.org")
        return response.text
    except requests.RequestException as e:
        print("Error:", e)
        
        
def check_firewall_rule_exists(port):
    firewall_manager = win32com.client.Dispatch("HNetCfg.FwMgr")
    firewall_policy = firewall_manager.LocalPolicy.CurrentProfile
    rules = firewall_policy.GloballyOpenPorts
    for rule in rules:
        if rule.Port == port:
            return True
    return False

def add_firewall_rule(port, protocol):
    command = 'netsh advfirewall firewall add rule name="HoangVPN {0}" dir=in action=allow protocol={1} localport={0}'.format(port, protocol)
    subprocess.run(command, check=False, creationflags=subprocess.CREATE_NO_WINDOW)
    
    command = 'netsh advfirewall firewall add rule name="HoangVPN {0}" dir=out action=allow protocol={1} localport={0}'.format(port, protocol)
    subprocess.run(command, check=False, creationflags=subprocess.CREATE_NO_WINDOW)

