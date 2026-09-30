# [H] Apache cxf-core: No restriction on attachment headers per message

## Summary
Severity: High
Advisory: GHSA-ghvc-7hp8-2g2v
CVE: CVE-2026-50645
CWE: CWE-400
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-06-12
Source: https://github.com/advisories/GHSA-ghvc-7hp8-2g2v
Type: github-advisory

## Affected
- Maven: `org.apache.cxf:cxf-core` — affected >=4.2.0 <4.2.2
- Maven: `org.apache.cxf:cxf-core` — affected >=4.0.0 <4.1.7
- Maven: `org.apache.cxf:cxf-core` — affected >=0 <3.6.12

## Details
There is no restriction on the amount of attachment headers that a message can contain when being deserialized by Apache CXF, which can lead to uncontrolled resource consumption or a denial of service attack. Users are recommended to upgrade to versions 4.2.2 or 4.1.7 or 3.6.12, which fix this issue by imposing a maximum default of 500 attachments per message.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-50645
- https://cxf.apache.org/security-advisories.data/CVE-2026-50645.txt
- https://github.com/apache/cxf
- https://lists.apache.org/thread/24zb7cqcvykhwm0j797dmdq25s61mj93
- http://www.openwall.com/lists/oss-security/2026/06/11/12
