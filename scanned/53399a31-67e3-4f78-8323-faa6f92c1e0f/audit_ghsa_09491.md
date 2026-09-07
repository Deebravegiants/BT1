# [C] Apache Wicket has a Session Fixation issue

## Summary
Severity: Critical
Advisory: GHSA-qpjw-p3jg-59j6
CVE: CVE-2026-40010
CWE: CWE-384
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-05-06
Source: https://github.com/advisories/GHSA-qpjw-p3jg-59j6
Type: github-advisory

## Affected
- Maven: `org.apache.wicket:wicket-auth-roles` — affected >=8.0.0-M1
- Maven: `org.apache.wicket:wicket-auth-roles` — affected >=9.0.0-M1
- Maven: `org.apache.wicket:wicket-auth-roles` — affected >=10.0.0-M1 <10.9.0

## Details
Missing invocation of Servlet http web request method changeSessionId after session binding can be exploited for a session fixation attack in Apache Wicket.

This issue affects Apache Wicket: from 8.0.0 through 8.17.0, 9.0.0, from 10.0.0 through 10.8.0.

Users are recommended to upgrade to version 10.9.0, which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-40010
- https://github.com/apache/wicket
- https://lists.apache.org/thread/61wsc0xdtfd5oozojfx7by9w3jwgkmv1
- http://www.openwall.com/lists/oss-security/2026/05/06/1
