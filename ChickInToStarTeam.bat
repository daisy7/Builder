set stcmdDir="C:\Program Files (x86)\Borland\StarTeam Cross-Platform Client 2009\stcmd"
set stName=zhangyang
set stPasswd=smee123456
set pjServer=172.16.200.11
set pjPort=49208
set "CHECK_IN=ci -p"
set "CREAT_LABEL=label -p"
set "ADD_FILE=add -p"
set ccDir=SCWB_300_10(003)/私有区/03 加工制造/编译区/SIT/output

set PROJECT_TYPE=%1
set GIT_TAG_NAME=%2
set PACKAGE_NAME=%3

::XCOPY /Y %PACKAGE_NAME%.zip "C:\003\私有区\03 加工制造\编译区\SIT\output" 1>nul 2>nul
::%stcmdDir% %CREAT_LABEL% "%stName%:%stPasswd%@%pjServer%:%pjPort%/%ccDir%" -r -x -nl "%GIT_TAG_NAME%" -d "%GIT_TAG_NAME%"
::%stcmdDir% %ADD_FILE% "%stName%:%stPasswd%@%pjServer%:%pjPort%/%ccDir%" -is -nologo -vl  "%GIT_TAG_NAME%" -d "%GIT_TAG_NAME%"
::%stcmdDir% %CHECK_IN% "%stName%:%stPasswd%@%pjServer%:%pjPort%/%ccDir%" -is -nologo -vl  "%GIT_TAG_NAME%" -r "%GIT_TAG_NAME%" -o %PACKAGE_NAME%.zip