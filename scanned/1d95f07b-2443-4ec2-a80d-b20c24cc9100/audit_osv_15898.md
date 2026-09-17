# [M] CVE-2019-20396

## Summary
Severity: Medium
Advisory: CVE-2019-20396
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2020-01-22
Source: https://osv.dev/vulnerability/CVE-2019-20396
Type: osv

## Details
A segmentation fault is present in yyparse in libyang before v1.0-r1 due to a malformed pattern statement value during lys_parse_path parsing.

## References
- https://lists.debian.org/debian-lts-announce/2023/09/msg00019.html
- https://github.com/CESNET/libyang/compare/v0.16-r3...v1.0-r1
- https://github.com/CESNET/libyang/commit/a1f17693904ed6fecc8902c747fc50a8f20e6af8
- https://github.com/CESNET/libyang/issues/740
