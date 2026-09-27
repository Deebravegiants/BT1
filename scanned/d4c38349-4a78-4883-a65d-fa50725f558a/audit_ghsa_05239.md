# [C] Apache CXF has JNDI Injection Vulnerability in JMSConfigFactory

## Summary
Severity: Critical
Advisory: GHSA-93g8-qqv3-mrx8
CVE: CVE-2026-50632
CWE: CWE-20, CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-06-12
Source: https://github.com/advisories/GHSA-93g8-qqv3-mrx8
Type: github-advisory

## Affected
- Maven: `org.apache.cxf:cxf-rt-transports-jms` — affected >=4.2.0 <4.2.2
- Maven: `org.apache.cxf:cxf-rt-transports-jms` — affected >=0 <4.1.7

## Details
A further incomplete fix for a previous advisory CVE-2026-44417 (Untrusted JMS configuration can lead to RCE) for Apache CXF has been identified, which can allow code execution capabilities, if untrusted users are allowed to configure JMS for Apache CXF. Users are recommended to upgrade to versions 4.2.2 or 4.1.7, which fixes this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-50632
- https://access.redhat.com/errata/RHSA-2026:37390
- https://access.redhat.com/security/cve/CVE-2026-50632
- https://bugzilla.redhat.com/show_bug.cgi?id=2488304
- https://github.com/apache/cxf
- https://lists.apache.org/thread/740ghch5z5y675cn2kzgtyo5k37n6qcw
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-50632.json
