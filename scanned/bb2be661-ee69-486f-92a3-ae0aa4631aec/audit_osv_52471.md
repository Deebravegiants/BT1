# [M] CVE-2021-47484

## Summary
Severity: Medium
Advisory: CVE-2021-47484
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-22
Source: https://osv.dev/vulnerability/CVE-2021-47484
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

octeontx2-af: Fix possible null pointer dereference.

This patch fixes possible null pointer dereference in files
"rvu_debugfs.c" and "rvu_nix.c"

## References
- https://git.kernel.org/stable/c/c2d4c543f74c90f883e8ec62a31973ae8807d354
- https://git.kernel.org/stable/c/f1e3cd1cc80204fd02b9e9843450925a2af90dc0
