# [M] uutils coreutils chcon Security Bypass and Mandatory Access Control (MAC) Inconsistency via TOCTOU Race Condition

## Summary
Severity: Medium
Advisory: CVE-2026-35376
Aliases: GHSA-6g8r-74qp-6859
CVSS: 4.5 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:L/I:L/A:L)
Published: 2026-04-22
Source: https://osv.dev/vulnerability/CVE-2026-35376
Type: osv

## Details
A Time-of-Check to Time-of-Use (TOCTOU) vulnerability exists in the chcon utility of uutils coreutils during recursive operations. The implementation resolves recursive targets using a fresh path lookup (via fts_accpath) rather than binding the traversal and label application to the specific directory state encountered during traversal. Because these operations are not anchored to file descriptors, a local attacker with write access to a directory tree can exploit timing-sensitive rename or symbolic link races to redirect a privileged recursive relabeling operation to unintended files or directories. This vulnerability breaks the hardening expectations for SELinux administration workflows and can lead to the unauthorized modification of security labels on sensitive system objects.

## References
- https://github.com/uutils
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/35xxx/CVE-2026-35376.json
- https://github.com/uutils/coreutils/releases/tag/0.8.0
- https://nvd.nist.gov/vuln/detail/CVE-2026-35376
- https://github.com/uutils/coreutils/pull/11402
- https://github.com/uutils/coreutils
