# [M] CVE-2016-4484

## Summary
Severity: Medium
Advisory: CVE-2016-4484
CVSS: 6.8 (CVSS:3.0/AV:P/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-01-23
Source: https://osv.dev/vulnerability/CVE-2016-4484
Type: osv

## Details
The Debian initrd script for the cryptsetup package 2:1.7.3-2 and earlier allows physically proximate attackers to gain shell access via many log in attempts with an invalid password.

## References
- http://www.securityfocus.com/bid/94315
- http://www.openwall.com/lists/oss-security/2016/11/14/13
- http://www.openwall.com/lists/oss-security/2016/11/15/1
- http://www.openwall.com/lists/oss-security/2016/11/15/4
- http://www.openwall.com/lists/oss-security/2016/11/16/6
- https://gitlab.com/cryptsetup/cryptsetup/commit/ef8a7d82d8d3716ae9b58179590f7908981fa0cb
- http://hmarco.org/bugs/CVE-2016-4484/CVE-2016-4484_cryptsetup_initrd_shell.html
