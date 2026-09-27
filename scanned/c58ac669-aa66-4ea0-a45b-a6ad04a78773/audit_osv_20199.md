# [M] CVE-2021-32135

## Summary
Severity: Medium
Advisory: CVE-2021-32135
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2021-09-13
Source: https://osv.dev/vulnerability/CVE-2021-32135
Type: osv

## Details
The trak_box_size function in GPAC 1.0.1 allows attackers to cause a denial of service (NULL pointer dereference) via a crafted file in the MP4Box command.

## References
- https://github.com/gpac/gpac/commit/b8f8b202d4fc23eb0ab4ce71ae96536ca6f5d3f8
- https://github.com/gpac/gpac/issues/1757
