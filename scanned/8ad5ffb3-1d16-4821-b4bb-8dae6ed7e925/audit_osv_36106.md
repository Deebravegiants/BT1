# [H] CVE-2026-20613

## Summary
Severity: High
Advisory: CVE-2026-20613
Aliases: GHSA-cq3j-qj2h-6rv3
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-01-23
Source: https://osv.dev/vulnerability/CVE-2026-20613
Type: osv

## Details
The ArchiveReader.extractContents() function used by cctl image load and container image load performs no pathname validation before extracting an archive member. This means that a carelessly or maliciously constructed archive can extract a file into any user-writable location on the system using relative pathnames. This issue is addressed in container 0.8.0 and containerization 0.21.0.

## References
- https://github.com/apple/containerization/security/advisories/GHSA-cq3j-qj2h-6rv3
