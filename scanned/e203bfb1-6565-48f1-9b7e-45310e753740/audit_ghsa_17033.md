# [H] XNIO denial of service vulnerability

## Summary
Severity: High
Advisory: GHSA-7f88-5hhx-67m2
CVE: CVE-2023-5685
CWE: CWE-400
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-03-22
Source: https://github.com/advisories/GHSA-7f88-5hhx-67m2
Type: github-advisory

## Affected
- Maven: `org.jboss.xnio:xnio-api` — affected >=0 <3.8.14.Final

## Details
A flaw was found in XNIO. The XNIO NotifierState that can cause a Stack Overflow Exception when the chain of notifier states becomes problematically large can lead to uncontrolled resource management and a possible denial of service (DoS). Version 3.8.14.Final is expected to contain a fix.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-5685
- https://github.com/xnio/xnio/commit/ffabdcdda508ef87aeadad5ca3f854e274d60ec1
- https://access.redhat.com/errata/RHSA-2023:7637
- https://access.redhat.com/errata/RHSA-2023:7638
- https://access.redhat.com/errata/RHSA-2023:7639
- https://access.redhat.com/errata/RHSA-2023:7641
- https://access.redhat.com/errata/RHSA-2024:10207
- https://access.redhat.com/errata/RHSA-2024:10208
- https://access.redhat.com/errata/RHSA-2024:2707
- https://access.redhat.com/security/cve/CVE-2023-5685
- https://bugzilla.redhat.com/show_bug.cgi?id=2241822
- https://github.com/xnio/xnio
- https://github.com/xnio/xnio/blob/3.8.13.Final/api/src/main/java/org/xnio/AbstractIoFuture.java#L249
- https://issues.redhat.com/browse/XNIO-423
