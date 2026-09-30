# [H] CVE-2019-9036

## Summary
Severity: High
Advisory: CVE-2019-9036
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-02-23
Source: https://osv.dev/vulnerability/CVE-2019-9036
Type: osv

## Details
An issue was discovered in libmatio.a in matio (aka MAT File I/O Library) 1.5.13. There is a heap-based buffer overflow in the function ReadNextFunctionHandle() in mat5.c.

## References
- https://github.com/tbeu/matio/issues/103
- https://github.com/TeamSeri0us/pocs/tree/master/matio
