# [M] CRI-O Path Traversal vulnerability

## Summary
Severity: Medium
Advisory: GHSA-hp5j-2585-qx6g
CVE: CVE-2025-0750
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:H (CVSS_V3)
Published: 2025-01-28
Source: https://github.com/advisories/GHSA-hp5j-2585-qx6g
Type: github-advisory

## Affected
- Go: `github.com/cri-o/cri-o` — affected >=0

## Details
A vulnerability was found in CRI-O. A path traversal issue in the log management functions (UnMountPodLogs and LinkContainerLogs) may allow an attacker with permissions to create and delete Pods to unmount arbitrary host paths, leading to node-level denial of service by unmounting critical system directories.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-0750
- https://access.redhat.com/errata/RHSA-2025:1122
- https://access.redhat.com/security/cve/CVE-2025-0750
- https://bugzilla.redhat.com/show_bug.cgi?id=2339405
- https://github.com/cri-o/cri-o
