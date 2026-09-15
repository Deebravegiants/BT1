# [C] Undertow HTTP server core doesn't properly validate the Host header in incoming HTTP requests

## Summary
Severity: Critical
Advisory: GHSA-j382-5jj3-vw4j
CVE: CVE-2025-12543
CWE: CWE-20
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:L (CVSS_V3)
Published: 2026-01-07
Source: https://github.com/advisories/GHSA-j382-5jj3-vw4j
Type: github-advisory

## Affected
- Maven: `io.undertow:undertow-core` — affected 2.4.0.Alpha1
- Maven: `io.undertow:undertow-core` — affected >=2.3.0.Alpha1 <2.3.21.Final
- Maven: `io.undertow:undertow-core` — affected >=0 <2.2.39.Final

## Details
A flaw was found in the Undertow HTTP server core, which is used in WildFly, JBoss EAP, and other Java applications. The Undertow library fails to properly validate the Host header in incoming HTTP requests. As a result, requests containing malformed or malicious Host headers are processed without rejection, enabling attackers to poison caches, perform internal network scans, or hijack user sessions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-12543
- https://github.com/undertow-io/undertow/pull/1860
- https://github.com/undertow-io/undertow/pull/1857
- https://issues.redhat.com/browse/UNDERTOW-2656
- https://github.com/undertow-io/undertow/releases/tag/2.3.21.Final
- https://github.com/undertow-io/undertow/releases/tag/2.2.39.Final
- https://github.com/undertow-io/undertow
- https://bugzilla.redhat.com/show_bug.cgi?id=2408784
- https://access.redhat.com/security/cve/CVE-2025-12543
- https://access.redhat.com/errata/RHSA-2026:4924
- https://access.redhat.com/errata/RHSA-2026:4917
- https://access.redhat.com/errata/RHSA-2026:4916
- https://access.redhat.com/errata/RHSA-2026:4915
- https://access.redhat.com/errata/RHSA-2026:3892
- https://access.redhat.com/errata/RHSA-2026:3891
- https://access.redhat.com/errata/RHSA-2026:3890
- https://access.redhat.com/errata/RHSA-2026:3889
- https://access.redhat.com/errata/RHSA-2026:0386
- https://access.redhat.com/errata/RHSA-2026:0384
- https://access.redhat.com/errata/RHSA-2026:0383
