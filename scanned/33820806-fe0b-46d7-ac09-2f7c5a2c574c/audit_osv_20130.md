# [M] CVE-2021-31262

## Summary
Severity: Medium
Advisory: CVE-2021-31262
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2021-04-19
Source: https://osv.dev/vulnerability/CVE-2021-31262
Type: osv

## Details
The AV1_DuplicateConfig function in GPAC 1.0.1 allows attackers to cause a denial of service (NULL pointer dereference) via a crafted file in the MP4Box command.

## References
- https://github.com/gpac/gpac/commit/b2eab95e07cb5819375a50358d4806a8813b6e50
- https://github.com/gpac/gpac/issues/1738
