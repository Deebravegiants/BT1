# [M] CVE-2020-22678

## Summary
Severity: Medium
Advisory: CVE-2020-22678
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2021-10-12
Source: https://osv.dev/vulnerability/CVE-2020-22678
Type: osv

## Details
An issue was discovered in gpac 0.8.0. The gf_media_nalu_remove_emulation_bytes function in av_parsers.c has a heap-based buffer overflow which can lead to a denial of service (DOS) via a crafted input.

## References
- https://github.com/gpac/gpac/issues/1339
