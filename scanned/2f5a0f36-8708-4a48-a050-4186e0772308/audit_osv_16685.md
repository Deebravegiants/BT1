# [C] CVE-2019-9037

## Summary
Severity: Critical
Advisory: CVE-2019-9037
CVSS: 9.1 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2019-02-23
Source: https://osv.dev/vulnerability/CVE-2019-9037
Type: osv

## Details
An issue was discovered in libmatio.a in matio (aka MAT File I/O Library) 1.5.13. There is a buffer over-read in the function Mat_VarPrint() in mat.c.

## References
- https://github.com/tbeu/matio/issues/103
- https://github.com/TeamSeri0us/pocs/tree/master/matio
