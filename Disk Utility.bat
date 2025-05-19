:: run this .bat file as administrator

@echo off
title Disk Utility
color 0A
setlocal enabledelayedexpansion

cd /d %~dp0

:: 使用 diskpart 將磁碟清單輸出到臨時文件
(
    echo list disk
) > diskpart_list.txt
diskpart /s diskpart_list.txt > disk_list_output.txt

(
    echo list volume
) > diskpart_list.txt
diskpart /s diskpart_list.txt > volume_list_output.txt

:: 顯示所有磁碟
echo list disk
echo.
echo Disk    Status Size    Free    
echo ------  ------ ------  --------

for /f "tokens=1-7 delims= " %%A in ('more +8 disk_list_output.txt') do (
    echo %%A %%B  %%C   %%D %%E  %%F %%G
)
echo.
pause
echo.

:: 顯示所有磁碟區
echo list volume
echo.
echo Ltr 
echo ----

for /f "tokens=3 delims= " %%A in ('more +8 volume_list_output.txt') do (
    echo %%A
)
echo.
pause
echo.

:: 選擇磁碟編號
set /p diskNum=Please Enter the Disk Number to Operate on (e.g. 2): 

:: 選擇清空磁碟的方法
echo.
echo Choose a Erase Option: 
echo 1. Clean
echo 2. Clean All (It takes a long time)
set /p cleanType=Please Enter Your Choice (1-2): 
if "%cleanType%"=="1" (
    set cleanCmd=clean
) else if "%cleanType%"=="2" (
    set cleanCmd=clean all
) else (
    echo Invalid Option, Clean is Selected by Default.
    set cleanCmd=clean
)

:: 選擇磁碟架構
echo.
echo Choose a Partition Scheme: 
echo 1. MBR
echo 2. GPT
set /p partType=Please Enter Your Choice (1-2): 
if "%partType%"=="1" (
    set convertCmd=convert mbr
) else if "%partType%"=="2" (
    set convertCmd=convert gpt
) else (
    echo Invalid Option, MBR is Selected by Default.
    set convertCmd=convert mbr
)

:: 選擇檔案系統格式
echo.
echo Choose a File System Format: 
echo 1. exFAT
echo 2. NTFS
echo 3. FAT32
set /p fsType=Please Enter Your Choice (1-3): 
if "%fsType%"=="1" (
    set fsCmd=exfat
) else if "%fsType%"=="2" (
    set fsCmd=ntfs
) else if "%fsType%"=="3" (
    set fsCmd=fat32
) else (
    echo Invalid Option, exFAT is Selected by Default.
    set fsCmd=exfat
)

:: 選擇快速格式化或標準格式化
echo.
echo Choose a Format Option: 
echo 1. Quick Format (quick)
echo 2. Full Format (It takes a long time)
set /p formatType=Please Enter Your Choice (1-2): 
if "%formatType%"=="1" (
    set formatCmd=quick
) else if "%formatType%"=="2" (
    set formatCmd=
) else (
    echo Invalid Option, Quick Format is Selected by Default.
    set formatCmd=quick
)

:: 輸入磁碟機代號
echo.
set /p driveLetter=Please Enter the Drive Letter to Assign (e.g. E): 

:: 生成 diskpart 命令脚本
(
    echo select disk %diskNum%
    echo %cleanCmd%
    echo %convertCmd%
    echo create partition primary
    echo format fs=%fsCmd% label="MyUSB" %formatCmd%
	:: MBR磁碟架構才需active指令
    echo active
    echo assign letter=%driveLetter%
) > diskpart_script.txt

:: 執行 diskpart 命令腳本
diskpart /s diskpart_script.txt

:: 清理臨時檔案
if exist diskpart_list.txt del diskpart_list.txt
if exist disk_list_output.txt del disk_list_output.txt
if exist volume_list_output.txt del volume_list_output.txt
if exist diskpart_script.txt del diskpart_script.txt

echo.
pause