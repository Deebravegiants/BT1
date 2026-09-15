# [M] JLSEC-2026-779

## Summary
Severity: Medium
Advisory: JLSEC-2026-779
Ecosystem: Julia
CVSS: 6.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:L)
Published: 2026-07-23
Source: https://osv.dev/vulnerability/JLSEC-2026-779
Type: osv

## Affected
- Julia: `libssh_jll` — affected >=0 <0.11.4+0

## Details
A malicious SCP server can send unexpected paths that could make the
client application override local files outside of working directory.
This could be misused to create malicious executable or configuration
files and make the user execute them under specific consequences.

This is the same issue as in OpenSSH, tracked as CVE-2019-6111.

## References
- https://access.redhat.com/errata/RHSA-2026:18160
- https://access.redhat.com/errata/RHSA-2026:18683
- https://access.redhat.com/security/cve/CVE-2026-0964
- https://bugzilla.redhat.com/show_bug.cgi?id=2436979
- https://www.libssh.org/2026/02/10/libssh-0-12-0-and-0-11-4-security-releases/
