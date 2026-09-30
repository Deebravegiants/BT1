# [M] CVE-2024-45778

## Summary
Severity: Medium
Advisory: CVE-2024-45778
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-03-03
Source: https://osv.dev/vulnerability/CVE-2024-45778
Type: osv

## Details
A stack overflow flaw was found when reading a BFS file system. A crafted BFS filesystem may lead to an uncontrolled loop, causing grub2 to crash.

## References
- https://access.redhat.com/security/cve/CVE-2024-45778
- https://bugzilla.redhat.com/show_bug.cgi?id=2345640
