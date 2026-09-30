# [C] Apache CXF JNDI Injection vulnerability in DispatchMDBMessageListenerImpl

## Summary
Severity: Critical
Advisory: GHSA-qp3f-rvj8-46c8
CVE: CVE-2026-50633
CWE: CWE-20, CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-06-12
Source: https://github.com/advisories/GHSA-qp3f-rvj8-46c8
Type: github-advisory

## Affected
- Maven: `org.apache.cxf:cxf-integration-jca` — affected >=4.2.0 <4.2.2
- Maven: `org.apache.cxf:cxf-integration-jca` — affected >=0 <4.1.7

## Details
A JNDI Injection vulnerability has been discovered in Apache CXF's JCA integration module, which can allow for code execution, if an attacker is able to manipulate the JCA deployment descriptor (ra.xml) or runtime activation parameters. Users are recommended to upgrade to versions 4.2.2 or 4.1.7, which fixes this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-50633
- https://access.redhat.com/errata/RHSA-2026:37390
- https://access.redhat.com/security/cve/CVE-2026-50633
- https://bugzilla.redhat.com/show_bug.cgi?id=2488307
- https://github.com/apache/cxf
- https://lists.apache.org/thread/1czhgovkgzdkyp3t61wthn0foogh2grf
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-50633.json
- http://www.openwall.com/lists/oss-security/2026/06/11/10
