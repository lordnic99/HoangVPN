import subprocess
import os
import common
import sys

os.chdir(os.path.dirname(__file__))
    
def wireguard_install():
    try:
        subprocess.run(["msiexec", "/i", "wireguard.msi", "/quiet", "DO_NOT_LAUNCH=True"], check=True, creationflags=subprocess.CREATE_NO_WINDOW)
        print("wireguard installed")
    except subprocess.CalledProcessError:
        print("wireguard install failed")
        
def wiresock_install():
    try:
        subprocess.run(["msiexec", "/i", "wiresock.msi", "/qn"], check=True, creationflags=subprocess.CREATE_NO_WINDOW)
        print("wiresock installed")
    except subprocess.CalledProcessError:
        print("wiresock install failed")
        
def is_app_installed():
    wireguard = False
    wiresock = False
    try:
        result = subprocess.run(["wmic", "product", "get", "name"], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
        installed_programs = result.stdout.lower()

        if "wireguard" in installed_programs:
            wireguard = True
        if "wiresock" in installed_programs:
            wiresock = True
            
        return (wireguard, wiresock)
    
    except Exception as e:
        print("Error:", e)
        return (False, False)
    

    
def main():
    try:
        subprocess.run(["redistx64.exe", "/q", "/norestart"], check=True, creationflags=subprocess.CREATE_NO_WINDOW)
    except subprocess.CalledProcessError as e:
        if e.returncode == 3010:
            pass # request reboot, it ok to passed
        else:
            raise # re-raise
    
    try:
        subprocess.run(["redistx86.exe", "/q", "/norestart"], check=True, creationflags=subprocess.CREATE_NO_WINDOW)
    except subprocess.CalledProcessError as e:
        if e.returncode == 3010:
            pass # request reboot, it ok to passed
        else:
            raise # re-raise
    
    wireguard, wiresock = is_app_installed()
    if not wireguard:
        print("installing wireguard")
        wireguard_install()
    else:
        print("wireguard OK")
    
    if not wiresock:
        print("installing wiresock")
        wiresock_install()
    else:
        print("wiresock OK")
        
    try:
        os.makedirs(r"C:\ProgramData\NT KERNEL\WireSock VPN Gateway")
    except FileExistsError:
        pass
    
    if not common.check_firewall_rule_exists("55555"):
        print("added port")
        common.add_firewall_rule("55555", "UDP")
    else:
        print("port ok")
    
    
        
    
        
        
