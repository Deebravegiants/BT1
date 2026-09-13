# [H] An improper link resolution flaw while extracting an archive can lead to changing the access control...

## Summary
Severity: High
Advisory: JLSEC-2025-235
Ecosystem: Julia
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2025-11-25
Source: https://osv.dev/vulnerability/JLSEC-2025-235
Type: osv

## Affected
- Julia: `LibArchive_jll` — affected >=0 <3.5.2+0

## Details
An improper link resolution flaw while extracting an archive can lead to changing the access control list (ACL) of the target of the link. An attacker may provide a malicious archive to a victim user, who would trigger this flaw when trying to extract the archive. A local attacker may use this flaw to change the ACL of a file on the system and gain more privileges.

## References
- https://access.redhat.com/security/cve/CVE-2021-23177
- https://bugzilla.redhat.com/show_bug.cgi?id=2024245
- https://github.com/libarchive/libarchive/commit/fba4f123cc456d2b2538f811bb831483bf336bad
- https://github.com/libarchive/libarchive/issues/1565
- https://lists.debian.org/debian-lts-announce/2022/11/msg00030.html
