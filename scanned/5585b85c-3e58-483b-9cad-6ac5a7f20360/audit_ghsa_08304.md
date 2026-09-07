# [M] Apache Wicket has a Cross-site Scripting issue

## Summary
Severity: Medium
Advisory: GHSA-5x9h-93gp-chpj
CVE: CVE-2026-42509
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-05-06
Source: https://github.com/advisories/GHSA-5x9h-93gp-chpj
Type: github-advisory

## Affected
- Maven: `org.apache.wicket:wicket-parent` — affected >=8.0.0-M1
- Maven: `org.apache.wicket:wicket-parent` — affected >=9.0.0-M1
- Maven: `org.apache.wicket:wicket-parent` — affected >=10.0.0-M1 <10.9.0

## Details
Improper Neutralization of Input During Web Page Generation ('Cross-site Scripting') vulnerability in Apache Wicket.

This issue affects Apache Wicket: from 8.0.0 through 8.17.0, 9.0.0, from 10.0.0 through 10.8.0.

Users are recommended to upgrade to version 10.9.0, which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-42509
- https://github.com/apache/wicket
- https://lists.apache.org/thread/52nrq4tt07gxz4r6sj5gyocz5s6bprjp
- http://www.openwall.com/lists/oss-security/2026/05/06/2
