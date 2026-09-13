# [M] CVE-2018-19329

## Summary
Severity: Medium
Advisory: CVE-2018-19329
CVSS: 4.9 (CVSS:3.0/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:H/A:N)
Published: 2018-11-17
Source: https://osv.dev/vulnerability/CVE-2018-19329
Type: osv

## Details
GreenCMS v2.3.0603 allows remote authenticated administrators to delete arbitrary files by modifying a base64-encoded pathname in an m=admin&c=media&a=delfilehandle&id= call, related to the m=admin&c=media&a=restorefile delete button.

## References
- https://github.com/GreenCMS/GreenCMS/issues/113
