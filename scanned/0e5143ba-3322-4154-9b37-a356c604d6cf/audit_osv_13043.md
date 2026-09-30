# [H] CVE-2018-17076

## Summary
Severity: High
Advisory: CVE-2018-17076
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-09-16
Source: https://osv.dev/vulnerability/CVE-2018-17076
Type: osv

## Details
GPP through 2.25 will try to use more memory space than is available on the stack, leading to a segmentation fault or possibly unspecified other impact via a crafted file.

## References
- https://github.com/logological/gpp/issues/26
