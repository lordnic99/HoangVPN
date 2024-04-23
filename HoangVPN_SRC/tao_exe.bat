
@echo off

python.exe -m nuitka --mingw64 .\run.py --standalone --onefile --remove-output --output-filename="HoangVPN"  --windows-icon-from-ico=ico.ico --windows-uac-admin  --windows-disable-console --include-data-file=resources/*=./
UPX\upx.exe --best HoangVPN.exe

echo Tao file exe thanh cong, kiem tra folder dist de su dung!

pause
