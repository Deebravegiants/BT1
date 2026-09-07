# [M] Unauthenticated user can retrieve the list of users through uorgsuggest.vm

## Summary
Severity: Medium
Advisory: GHSA-97jg-43c9-q6pf
CVE: CVE-2022-24819
CWE: CWE-359
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-04-08
Source: https://github.com/advisories/GHSA-97jg-43c9-q6pf
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-web-templates` — affected >=0 <12.10.11
- Maven: `org.xwiki.platform:xwiki-platform-web-templates` — affected >=13.0.0 <13.4.4
- Maven: `org.xwiki.platform:xwiki-platform-web-templates` — affected >=13.5.0 <13.9

## Details
A guest user without the right to view pages of the wiki can still list documents related to users of the wiki. The problem has been patched in XWiki versions 12.10.11, 13.4.4, and 13.9-rc-1. There is no known workaround for this problem.

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-97jg-43c9-q6pf
- https://nvd.nist.gov/vuln/detail/CVE-2022-24819
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-18850
