# [M] CVE-2020-11585

## Summary
Severity: Medium
Advisory: CVE-2020-11585
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2020-04-06
Source: https://osv.dev/vulnerability/CVE-2020-11585
Type: osv

## Details
There is an information disclosure issue in DNN (formerly DotNetNuke) 9.5 within the built-in Activity-Feed/Messaging/Userid/ Message Center module. A registered user is able to enumerate any file in the Admin File Manager (other than ones contained in a secure folder) by sending themselves a message with the file attached, e.g., by using an arbitrary small integer value in the fileIds parameter.

## References
- https://neff.blog/2020/04/04/dotnetnuke-9-5-file-path-information-disclosure/
