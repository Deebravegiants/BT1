# [M] CVE-2021-31260

## Summary
Severity: Medium
Advisory: CVE-2021-31260
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2021-04-19
Source: https://osv.dev/vulnerability/CVE-2021-31260
Type: osv

## Details
The MergeTrack function in GPAC 1.0.1 allows attackers to cause a denial of service (NULL pointer dereference) via a crafted file in the MP4Box command.

## References
- https://github.com/gpac/gpac/commit/df8fffd839fe5ae9acd82d26fd48280a397411d9
- https://github.com/gpac/gpac/issues/1736
