# [C] CVE-2019-9195

## Summary
Severity: Critical
Advisory: CVE-2019-9195
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-02-26
Source: https://osv.dev/vulnerability/CVE-2019-9195
Type: osv

## Details
util/src/zip.rs in Grin before 1.0.2 mishandles suspicious files. An attacker can execute arbitrary code via directory traversal in a ZIP archive.

## References
- https://github.com/mimblewimble/grin/releases/tag/v1.0.2
- https://www.grin-forum.org/t/critical-vulnerability-in-grin-1-0-1-and-older-fixed-in-1-0-2/4343
- https://github.com/mimblewimble/grin/pull/2624
