# [C] Apache CXF has an LDAP injection vulnerability

## Summary
Severity: Critical
Advisory: GHSA-pg32-686q-qh6x
CVE: CVE-2026-44930
CWE: CWE-90
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-26
Source: https://github.com/advisories/GHSA-pg32-686q-qh6x
Type: github-advisory

## Affected
- Maven: `org.apache.cxf.services.xkms:cxf-services-xkms-x509-repo-ldap` — affected >=4.2.0 <4.2.1
- Maven: `org.apache.cxf.services.xkms:cxf-services-xkms-x509-repo-ldap` — affected >=4.1.0 <4.1.6
- Maven: `org.apache.cxf.services.xkms:cxf-services-xkms-x509-repo-ldap` — affected >=0 <3.6.11

## Details
An LDAP injection vulnerability in the LDAP Certificate repository of the XKMS server in Apache CXF may allow an attacker to retrieve arbitrary certificates from the repository. 
Users are recommended to upgrade to versions 4.2.1, 4.1.6 or 3.6.11, which fix this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-44930
- https://github.com/apache/cxf
- https://lists.apache.org/thread/c1zqxppo1m5z3kbdhjn5p991zk09ynkh
- http://www.openwall.com/lists/oss-security/2026/05/22/9
