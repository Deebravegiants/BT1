# [C] CVE-2020-19751

## Summary
Severity: Critical
Advisory: CVE-2020-19751
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2021-09-07
Source: https://osv.dev/vulnerability/CVE-2020-19751
Type: osv

## Details
An issue was discovered in gpac 0.8.0. The gf_odf_del_ipmp_tool function in odf_code.c has a heap-based buffer over-read.

## References
- https://github.com/gpac/gpac/issues/1272
- https://cwe.mitre.org/data/definitions/126.html
