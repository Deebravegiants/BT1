# [C] CVE-2021-3199

## Summary
Severity: Critical
Advisory: CVE-2021-3199
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-01-26
Source: https://osv.dev/vulnerability/CVE-2021-3199
Type: osv

## Details
Directory traversal with remote code execution can occur in /upload in ONLYOFFICE Document Server before 5.6.3, when JWT is used, via a /.. sequence in an image upload parameter.

## References
- https://github.com/ONLYOFFICE/DocumentServer/blob/903fe5ab7a275bd69c3c3346af2d21cf87ebeabf/CHANGELOG.md#563
- https://github.com/moehw/poc_exploits/tree/master/CVE-2021-3199/poc_uploadImageFile.py
- https://github.com/nola-milkin/poc_exploits/blob/master/CVE-2021-3199/poc_uploadImageFile.py
