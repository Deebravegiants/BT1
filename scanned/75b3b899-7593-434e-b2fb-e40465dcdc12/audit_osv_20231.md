# [M] CVE-2021-32437

## Summary
Severity: Medium
Advisory: CVE-2021-32437
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2021-08-11
Source: https://osv.dev/vulnerability/CVE-2021-32437
Type: osv

## Details
The gf_hinter_finalize function in GPAC 1.0.1 allows attackers to cause a denial of service (NULL pointer dereference) via a crafted file in the MP4Box command.

## References
- https://github.com/gpac/gpac/issues/1770
- https://github.com/gpac/gpac/commit/1653f31cf874eb6df964bea88d58d8e9b98b485e
