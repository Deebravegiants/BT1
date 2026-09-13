# [M] CVE-2021-40575

## Summary
Severity: Medium
Advisory: CVE-2021-40575
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-01-13
Source: https://osv.dev/vulnerability/CVE-2021-40575
Type: osv

## Details
The binary MP4Box in Gpac 1.0.1 has a null pointer dereference vulnerability in the mpgviddmx_process function in reframe_mpgvid.c, which allows attackers to cause a denial of service. This vulnerability is possibly due to an incomplete fix for CVE-2021-40566.

## References
- https://www.debian.org/security/2023/dsa-5411
- https://github.com/gpac/gpac/issues/1905
- https://github.com/gpac/gpac/commit/5f2c2a16d30229b6241f02fa28e3d6b810d64858
