# [H] Apache Wicket has an Exposure of Sensitive Information to an Unauthorized Actor vulnerability

## Summary
Severity: High
Advisory: GHSA-jvv4-8wxx-m5r6
CVE: CVE-2026-43646
CWE: CWE-200
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-05-06
Source: https://github.com/advisories/GHSA-jvv4-8wxx-m5r6
Type: github-advisory

## Affected
- Maven: `org.apache.wicket:wicket-parent` — affected >=8.0.0-M1
- Maven: `org.apache.wicket:wicket-parent` — affected >=9.0.0-M1
- Maven: `org.apache.wicket:wicket-parent` — affected >=10.0.0-M1 <10.9.0

## Details
Exposure of Sensitive Information to an Unauthorized Actor vulnerability in Apache Wicket.

This issue affects Apache Wicket: from 8.0.0 through 8.17.0, from 9.0.0 through 9.22.0, from 10.0.0 through 10.8.0.

Users are recommended to upgrade to version 10.9.0, which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-43646
- https://github.com/apache/wicket
- https://lists.apache.org/thread/6zqcvjyz4lsqty1z2g5hg7pl5fqk88rs
- http://www.openwall.com/lists/oss-security/2026/05/06/3
