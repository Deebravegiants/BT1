# [M] Apache Struts vulnerable to memory exhaustion

## Summary
Severity: Medium
Advisory: GHSA-8f6x-v685-g2xc
CVE: CVE-2023-34149
CWE: CWE-770
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-06-14
Source: https://github.com/advisories/GHSA-8f6x-v685-g2xc
Type: github-advisory

## Affected
- Maven: `org.apache.struts:struts2-core` — affected >=0 <2.5.31
- Maven: `org.apache.struts:struts2-core` — affected >=6.0.0 <6.1.2.1

## Details
Denial of service via out of memory (OOM) owing to not properly checking of list bounds. When a Multipart request has non-file normal form fields, Struts used to bring them into memory as Strings without checking their sizes. This could lead to OOM if developer has set struts.multipart.maxSize to a value equal or greater than the available memory.

Upgrade to Struts 2.5.31 or 6.1.2.1 or greater.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-34149
- https://github.com/apache/struts/commit/2d6f1bc0a6f5ac575a56784ac6461816b67c4f21
- https://cwiki.apache.org/confluence/display/WW/S2-063
- https://github.com/apache/struts
- https://github.com/apache/struts/releases/tag/STRUTS_2_5_31
- https://github.com/apache/struts/releases/tag/STRUTS_6_1_2_1
- https://security.netapp.com/advisory/ntap-20230706-0005
- http://www.openwall.com/lists/oss-security/2023/06/14/2
