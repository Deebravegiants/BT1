# [C] Incorrect Default Permissions in Apache JSPWiki

## Summary
Severity: Critical
Advisory: GHSA-8gw6-w5rw-4g5c
CVE: CVE-2021-44140
CWE: CWE-276
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2021-11-29
Source: https://github.com/advisories/GHSA-8gw6-w5rw-4g5c
Type: github-advisory

## Affected
- Maven: `org.apache.jspwiki:jspwiki-main` — affected >=0 <2.11.0

## Details
Remote attackers may delete arbitrary files in a system hosting a JSPWiki instance, versions up to 2.11.0.M8, by using a carefuly crafted http request on logout, given that those files are reachable to the user running the JSPWiki instance. Apache JSPWiki users should upgrade to 2.11.0 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-44140
- https://github.com/apache/jspwiki
- https://jspwiki-wiki.apache.org/Wiki.jsp?page=CVE-2021-44140
- https://lists.apache.org/thread/5qglpjdhvobppx7j550lf1sk28f6011t
