# [M] CVE-2019-6458

## Summary
Severity: Medium
Advisory: CVE-2019-6458
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-01-16
Source: https://osv.dev/vulnerability/CVE-2019-6458
Type: osv

## Details
An issue was discovered in GNU Recutils 1.8. There is a memory leak in rec_buf_new in rec-buf.c when called from rec_parse_rset in rec-parser.c in librec.a.

## References
- https://github.com/TeamSeri0us/pocs/tree/master/recutils
