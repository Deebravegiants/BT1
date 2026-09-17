# [M] CVE-2021-33365

## Summary
Severity: Medium
Advisory: CVE-2021-33365
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2021-09-13
Source: https://osv.dev/vulnerability/CVE-2021-33365
Type: osv

## Details
Memory leak in the gf_isom_get_root_od function in MP4Box in GPAC 1.0.1 allows attackers to read memory via a crafted file.

## References
- https://www.debian.org/security/2023/dsa-5411
- https://github.com/gpac/gpac/commit/984787de3d414a5f7d43d0b4584d9469dff2a5a5
- https://github.com/gpac/gpac/issues/1784
