# [M] CVE-2021-44591

## Summary
Severity: Medium
Advisory: CVE-2021-44591
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-01-06
Source: https://osv.dev/vulnerability/CVE-2021-44591
Type: osv

## Details
In libming 0.4.8, the parseSWF_DEFINELOSSLESS2 function in util/parser.c lacks a boundary check that would lead to denial-of-service attacks via a crafted SWF file.

## References
- https://github.com/libming/libming
- https://github.com/libming/libming/issues/235
