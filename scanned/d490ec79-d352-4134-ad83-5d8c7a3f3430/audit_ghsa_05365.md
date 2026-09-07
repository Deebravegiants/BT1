# [H] Apache Struts 2 is Missing XML Validation

## Summary
Severity: High
Advisory: GHSA-qcfc-hmrc-59x7
CVE: CVE-2025-68493
CWE: CWE-112, CWE-611
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:H (CVSS_V3)
Published: 2026-01-11
Source: https://github.com/advisories/GHSA-qcfc-hmrc-59x7
Type: github-advisory

## Affected
- Maven: `org.apache.struts:struts2-core` — affected >=2.0.0
- Maven: `org.apache.struts:struts2-core` — affected >=2.5.0
- Maven: `org.apache.struts:struts2-core` — affected >=6.0.0 <6.1.1
- Maven: `com.opensymphony:xwork` — affected >=2.0.0
- Maven: `org.apache.struts.xwork:xwork-core` — affected >=2.2.1

## Details
Missing XML Validation vulnerability in Apache Struts, Apache Struts.

This issue affects Apache Struts: from 2.0.0 before 2.2.1; Apache Struts: from 2.2.1 through 6.1.0.

Users are recommended to upgrade to version 6.1.1, which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-68493
- https://cwiki.apache.org/confluence/display/WW/S2-069
- https://github.com/apache/struts
- http://www.openwall.com/lists/oss-security/2026/01/11/2
