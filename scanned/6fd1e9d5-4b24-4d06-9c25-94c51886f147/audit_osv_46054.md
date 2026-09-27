# [C] Rsync versions before 3.4.3 contain a time-of-check to time-of-use (TOCTOU) race condition in daemon...

## Summary
Severity: Critical
Advisory: JLSEC-2026-626
Ecosystem: Julia
CVSS: 9.0 (CVSS:4.0/AV:L/AC:H/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/JLSEC-2026-626
Type: osv

## Affected
- Julia: `rsync_jll` — affected >=0 <3.4.4+0

## Details
Rsync versions before 3.4.3 contain a time-of-check to time-of-use (TOCTOU) race condition in daemon file handling that allows attackers to redirect file writes outside intended directories by replacing parent directory components with symbolic links. Attackers with write access to a module path can exploit this race condition to create or overwrite arbitrary files, potentially modifying sensitive system files and achieving privilege escalation when the daemon runs with elevated privileges. This vulnerability can only be triggered if the chroot setting is false.

## References
- https://access.redhat.com/errata/RHSA-2026:26332
- https://access.redhat.com/errata/RHSA-2026:26408
- https://access.redhat.com/errata/RHSA-2026:26410
- https://access.redhat.com/errata/RHSA-2026:29197
- https://access.redhat.com/security/cve/CVE-2026-29518
- https://bugzilla.redhat.com/show_bug.cgi?id=2469055
- https://github.com/RsyncProject/rsync/pull/895/changes/8471fdd1561049ef5f58df44a1811a50bd9a531d
- https://github.com/RsyncProject/rsync/releases/tag/v3.4.3
- https://github.com/advisories/GHSA-pfv9-gp3h-73xv
- https://michael.stapelberg.ch/posts/2026-05-24-minimal-memory-safe-go-rsync-vulns
- https://michael.stapelberg.ch/posts/2026-05-24-minimal-memory-safe-go-rsync-vulns/
- https://nvd.nist.gov/vuln/detail/CVE-2026-29518
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-29518.json
- https://www.vulncheck.com/advisories/rsync-toctou-race-condition-allows-symlink-based-arbitrary-file-write
