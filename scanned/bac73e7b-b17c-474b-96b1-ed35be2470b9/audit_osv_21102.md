# [M] CVE-2021-40572

## Summary
Severity: Medium
Advisory: CVE-2021-40572
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-01-13
Source: https://osv.dev/vulnerability/CVE-2021-40572
Type: osv

## Details
The binary MP4Box in Gpac 1.0.1 has a double-free bug in the av1dmx_finalize function in reframe_av1.c, which allows attackers to cause a denial of service.

## References
- https://www.debian.org/security/2023/dsa-5411
- https://github.com/gpac/gpac/issues/1893
- https://github.com/gpac/gpac/commit/7bb1b4a4dd23c885f9db9f577dfe79ecc5433109
