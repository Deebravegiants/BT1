# [M] CVE-2021-33366

## Summary
Severity: Medium
Advisory: CVE-2021-33366
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2021-09-13
Source: https://osv.dev/vulnerability/CVE-2021-33366
Type: osv

## Details
Memory leak in the gf_isom_oinf_read_entry function in MP4Box in GPAC 1.0.1 allows attackers to read memory via a crafted file.

## References
- https://www.debian.org/security/2023/dsa-5411
- https://github.com/gpac/gpac/commit/0a85029d694f992f3631e2f249e4999daee15cbf
- https://github.com/gpac/gpac/issues/1785
