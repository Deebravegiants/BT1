# [M] CVE-2021-31256

## Summary
Severity: Medium
Advisory: CVE-2021-31256
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2021-04-19
Source: https://osv.dev/vulnerability/CVE-2021-31256
Type: osv

## Details
Memory leak in the stbl_GetSampleInfos function in MP4Box in GPAC 1.0.1 allows attackers to read memory via a crafted file.

## References
- https://github.com/gpac/gpac/commit/2da2f68bffd51d89b1d272d22aa8cc023c1c066e
- https://github.com/gpac/gpac/issues/1705
