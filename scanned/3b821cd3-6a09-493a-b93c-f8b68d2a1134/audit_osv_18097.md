# [M] CVE-2020-23932

## Summary
Severity: Medium
Advisory: CVE-2020-23932
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2021-04-21
Source: https://osv.dev/vulnerability/CVE-2020-23932
Type: osv

## Details
An issue was discovered in gpac before 1.0.1. A NULL pointer dereference exists in the function dump_isom_sdp located in filedump.c. It allows an attacker to cause Denial of Service.

## References
- https://github.com/gpac/gpac/commit/ce01bd15f711d4575b7424b54b3a395ec64c1784
- https://github.com/gpac/gpac/issues/1566
