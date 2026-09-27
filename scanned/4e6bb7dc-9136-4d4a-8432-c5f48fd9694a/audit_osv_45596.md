# [M] TOCTOU in GNU tar allows unauthorized file modification by a local attacker

## Summary
Severity: Medium
Advisory: JLSEC-2026-1344
Ecosystem: Julia
CVSS: 4.4 (CVSS:3.1/AV:L/AC:H/PR:L/UI:R/S:U/C:N/I:H/A:N)
Published: 2026-08-18
Source: https://osv.dev/vulnerability/JLSEC-2026-1344
Type: osv

## Affected
- Julia: `Tar_jll` — affected >=1.35.0+0

## Details
A TOCTOU (Time-of-Check Time-of-Use) vulnerability in GNU tar's incremental dumpdir 'X' rename handling allows a local attacker with write access to a directory being backed up to influence the restore process if the attacker has access to the system where the restore is being performed. During restoration, files or directories may be created, renamed or overwritten outside the intended extraction directory. This could lead to unauthorized file modification or, in some cases, privilege escalation. Exploitation does not require the attacker to modify or craft the archive, and standard backup and restore workflows—including extracting into a newly created directory without using the -P option do not mitigate the issue.

## References
- https://access.redhat.com/errata/RHSA-2026:49361
- https://access.redhat.com/security/cve/CVE-2026-18477
- https://bugzilla.redhat.com/show_bug.cgi?id=2509735
