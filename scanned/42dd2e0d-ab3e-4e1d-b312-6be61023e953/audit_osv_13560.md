# [H] CVE-2018-20337

## Summary
Severity: High
Advisory: CVE-2018-20337
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-12-21
Source: https://osv.dev/vulnerability/CVE-2018-20337
Type: osv

## Details
There is a stack-based buffer overflow in the parse_makernote function of dcraw_common.cpp in LibRaw 0.19.1. Crafted input will lead to a denial of service or possibly unspecified other impact.

## References
- https://usn.ubuntu.com/3989-1/
- https://github.com/LibRaw/LibRaw/issues/192
