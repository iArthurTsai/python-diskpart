Make sure the file 'Disk Utility.ico' is in the same directory as 'Disk Utility.py' and 'Disk Utility.exe'
Build Command: pyinstaller --noconsole --onefile --icon="Disk Utility.ico" --clean --add-data "Disk Utility.ico;." "Disk Utility.py" > build_log.txt 2>&1
