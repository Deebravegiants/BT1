# [M] Improper Input Validation in org.wildfly:wildfly-undertow

## Summary
Severity: Medium
Advisory: GHSA-fmr4-w67p-vh8x
CVE: CVE-2018-1047
CWE: CWE-20, CWE-22
Ecosystem: Maven
CVSS: CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2018-10-19
Source: https://github.com/advisories/GHSA-fmr4-w67p-vh8x
Type: github-advisory

## Affected
- Maven: `org.wildfly:wildfly-undertow` — affected >=0 <12.0.0

## Details
A flaw was found in Wildfly 9.x. A path traversal vulnerability through the org.wildfly.extension.undertow.deployment.ServletResourceManager.getResource method could lead to information disclosure of arbitrary local files.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1047
- https://access.redhat.com/errata/RHSA-2018:1247
- https://access.redhat.com/errata/RHSA-2018:1248
- https://access.redhat.com/errata/RHSA-2018:1249
- https://access.redhat.com/errata/RHSA-2018:1251
- https://access.redhat.com/errata/RHSA-2018:2938
- https://access.redhat.com/security/cve/CVE-2018-1047
- https://bugzilla.redhat.com/show_bug.cgi?id=1528361
- https://github.com/advisories/GHSA-fmr4-w67p-vh8x
- https://issues.jboss.org/browse/WFLY-9620
