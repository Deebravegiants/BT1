# [M] Undertow Path Traversal vulnerability

## Summary
Severity: Medium
Advisory: GHSA-v76w-3ph8-vm66
CVE: CVE-2024-1459
CWE: CWE-24
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2024-02-12
Source: https://github.com/advisories/GHSA-v76w-3ph8-vm66
Type: github-advisory

## Affected
- Maven: `io.undertow:undertow-core` — affected >=0 <2.2.31.Final
- Maven: `io.undertow:undertow-core` — affected >=2.3.0.Alpha1 <2.3.12.Final

## Details
A path traversal vulnerability was found in Undertow. This issue may allow a remote attacker to append a specially-crafted sequence to an HTTP request for an application deployed to JBoss EAP, which may permit access to privileged or restricted files and directories.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-1459
- https://github.com/undertow-io/undertow/pull/1556
- https://github.com/undertow-io/undertow/commit/40bb3314f013247af8e222870bd5045ca8650c5c
- https://github.com/undertow-io/undertow/commit/54f3e4325425c472f5af5fc973e02df83d7a711a
- https://access.redhat.com/errata/RHSA-2024:1674
- https://access.redhat.com/errata/RHSA-2024:1675
- https://access.redhat.com/errata/RHSA-2024:1676
- https://access.redhat.com/errata/RHSA-2024:1677
- https://access.redhat.com/errata/RHSA-2024:2763
- https://access.redhat.com/errata/RHSA-2024:2764
- https://access.redhat.com/security/cve/CVE-2024-1459
- https://bugzilla.redhat.com/show_bug.cgi?id=2259475
- https://issues.redhat.com/browse/UNDERTOW-2339
- https://security.netapp.com/advisory/ntap-20241122-0008
