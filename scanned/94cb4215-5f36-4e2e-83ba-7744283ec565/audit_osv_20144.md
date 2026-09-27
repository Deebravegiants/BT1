# [H] CVE-2021-31566

## Summary
Severity: High
Advisory: CVE-2021-31566
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2022-08-23
Source: https://osv.dev/vulnerability/CVE-2021-31566
Type: osv

## Details
An improper link resolution flaw can occur while extracting an archive leading to changing modes, times, access control lists, and flags of a file outside of the archive. An attacker may provide a malicious archive to a victim user, who would trigger this flaw when trying to extract the archive. A local attacker may use this flaw to gain more privileges in a system.

## References
- https://access.redhat.com/security/cve/CVE-2021-31566
- https://lists.debian.org/debian-lts-announce/2022/11/msg00030.html
- https://bugzilla.redhat.com/show_bug.cgi?id=2024237
- https://github.com/libarchive/libarchive/commit/b41daecb5ccb4c8e3b2c53fd6147109fc12c3043
- https://github.com/libarchive/libarchive/issues/1566
