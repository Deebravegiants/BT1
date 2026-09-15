# [H] CVE-2021-36417

## Summary
Severity: High
Advisory: CVE-2021-36417
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2022-01-12
Source: https://osv.dev/vulnerability/CVE-2021-36417
Type: osv

## Details
A heap-based buffer overflow vulnerability exists in GPAC v1.0.1 in the gf_isom_dovi_config_get function in MP4Box, which causes a denial of service or execute arbitrary code via a crafted file.

## References
- https://www.debian.org/security/2023/dsa-5411
- https://github.com/gpac/gpac/issues/1846
