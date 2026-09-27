# [C] CVE-2017-5539

## Summary
Severity: Critical
Advisory: CVE-2017-5539
CVSS: 9.1 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2017-01-23
Source: https://osv.dev/vulnerability/CVE-2017-5539
Type: osv

## Details
The patch for directory traversal (CVE-2017-5480) in b2evolution version 6.8.4-stable has a bypass vulnerability. An attacker can use ..\/ to bypass the filter rule. Then, this attacker can exploit this vulnerability to delete or read any files on the server. It can also be used to determine whether a file exists.

## References
- http://www.securityfocus.com/bid/95700
- http://b2evolution.net/downloads/6-8-5
- https://github.com/b2evolution/b2evolution/commit/e35f7c195d8c1103d2d981a48cda5ab45ecac48a
- https://github.com/b2evolution/b2evolution/issues/36
