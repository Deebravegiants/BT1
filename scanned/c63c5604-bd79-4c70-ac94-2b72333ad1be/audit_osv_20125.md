# [M] CVE-2021-31257

## Summary
Severity: Medium
Advisory: CVE-2021-31257
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2021-04-19
Source: https://osv.dev/vulnerability/CVE-2021-31257
Type: osv

## Details
The HintFile function in GPAC 1.0.1 allows attackers to cause a denial of service (NULL pointer dereference) via a crafted file in the MP4Box command.

## References
- https://github.com/gpac/gpac/commit/87afe070cd6866df7fe80f11b26ef75161de85e0
- https://github.com/gpac/gpac/issues/1734
