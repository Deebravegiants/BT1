# [M] CVE-2021-32138

## Summary
Severity: Medium
Advisory: CVE-2021-32138
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2021-09-13
Source: https://osv.dev/vulnerability/CVE-2021-32138
Type: osv

## Details
The DumpTrackInfo function in GPAC 1.0.1 allows attackers to cause a denial of service (NULL pointer dereference) via a crafted file in the MP4Box command.

## References
- https://github.com/gpac/gpac/commit/289ffce3e0d224d314f5f92a744d5fe35999f20b
- https://github.com/gpac/gpac/issues/1767
