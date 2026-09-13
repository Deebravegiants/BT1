# [H] An improper link resolution flaw can occur while extracting an archive leading to changing modes,...

## Summary
Severity: High
Advisory: JLSEC-2025-236
Ecosystem: Julia
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2025-11-25
Source: https://osv.dev/vulnerability/JLSEC-2025-236
Type: osv

## Affected
- Julia: `LibArchive_jll` — affected >=0 <3.5.2+0

## Details
An improper link resolution flaw can occur while extracting an archive leading to changing modes, times, access control lists, and flags of a file outside of the archive. An attacker may provide a malicious archive to a victim user, who would trigger this flaw when trying to extract the archive. A local attacker may use this flaw to gain more privileges in a system.

## References
- https://access.redhat.com/security/cve/CVE-2021-31566
- https://bugzilla.redhat.com/show_bug.cgi?id=2024237
- https://github.com/libarchive/libarchive/commit/b41daecb5ccb4c8e3b2c53fd6147109fc12c3043
- https://github.com/libarchive/libarchive/issues/1566
- https://lists.debian.org/debian-lts-announce/2022/11/msg00030.html
