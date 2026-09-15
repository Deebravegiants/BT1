# [M] CVE-2021-40564

## Summary
Severity: Medium
Advisory: CVE-2021-40564
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-01-12
Source: https://osv.dev/vulnerability/CVE-2021-40564
Type: osv

## Details
A Segmentation fault caused by null pointer dereference vulnerability eists in Gpac through 1.0.2 via the avc_parse_slice function in av_parsers.c when using mp4box, which causes a denial of service.

## References
- https://github.com/gpac/gpac/issues/1898
- https://www.debian.org/security/2023/dsa-5411
- https://github.com/gpac/gpac/commit/cf6771c857eb9a290e2c19ddacfdd3ed98b27618
