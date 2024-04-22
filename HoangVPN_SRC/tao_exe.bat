
@echo off

REM pyinstaller .\run.py -w --noconsole --noconfirm -n HoangVPN --icon=ico.ico --add-data "rathole.exe:." --add-data "wiresock.msi:." --add-REM data "wireguard.msi:." --add-data "nssm.exe:." --add-data "rathole_client.exe:." --add-data "api.json:." --upx-dir UPX

python.exe -m nuitka --mingw64 .\run.py --standalone --onefile --remove-output --output-filename="HoangVPN"  --windows-icon-from-ico=ico.ico --windows-uac-admin  --windows-disable-console --include-data-file=resources/*=./ --plugin-enable=upx --upx-binary=UPX

echo Tao file exe thanh cong, kiem tra folder dist de su dung!
pause