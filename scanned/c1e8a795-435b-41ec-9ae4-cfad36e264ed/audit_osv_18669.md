# [C] CVE-2020-35173

## Summary
Severity: Critical
Advisory: CVE-2020-35173
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-12-30
Source: https://osv.dev/vulnerability/CVE-2020-35173
Type: osv

## Details
The Amaze File Manager application before 3.4.2 for Android does not properly restrict intents for controlling the FTP server (aka services.ftpservice.FTPReceiver.ACTION_START_FTPSERVER and services.ftpservice.FTPReceiver.ACTION_STOP_FTPSERVER).

## References
- https://github.com/TeamAmaze/AmazeFileManager/pull/1815
- https://play.google.com/store/apps/details?id=com.amaze.filemanager&hl=en_US&gl=US
- https://github.com/TeamAmaze/AmazeFileManager/compare/v3.4.1...v3.4.2
