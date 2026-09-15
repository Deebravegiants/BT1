# [M] CVE-2018-6791

## Summary
Severity: Medium
Advisory: CVE-2018-6791
CVSS: 6.8 (CVSS:3.0/AV:P/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-02-07
Source: https://osv.dev/vulnerability/CVE-2018-6791
Type: osv

## Details
An issue was discovered in soliduiserver/deviceserviceaction.cpp in KDE Plasma Workspace before 5.12.0. When a vfat thumbdrive that contains `` or $() in its volume label is plugged in and mounted through the device notifier, it's interpreted as a shell command, leading to a possibility of arbitrary command execution. An example of an offending volume label is "$(touch b)" -- this will create a file called b in the home folder.

## References
- https://cgit.kde.org/plasma-workspace.git/commit/?id=9db872df82c258315c6ebad800af59e81ffb9212
- https://www.debian.org/security/2018/dsa-4116
- https://bugs.kde.org/show_bug.cgi?id=389815
