# [M] CVE-2021-40565

## Summary
Severity: Medium
Advisory: CVE-2021-40565
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-01-12
Source: https://osv.dev/vulnerability/CVE-2021-40565
Type: osv

## Details
A Segmentation fault caused by a null pointer dereference vulnerability exists in Gpac through 1.0.1 via the gf_avc_parse_nalu function in av_parsers.c when using mp4box, which causes a denial of service.

## References
- https://github.com/gpac/gpac/issues/1902
- https://www.debian.org/security/2023/dsa-5411
- https://github.com/gpac/gpac/commit/893fb99b606eebfae46cde151846a980e689039b
