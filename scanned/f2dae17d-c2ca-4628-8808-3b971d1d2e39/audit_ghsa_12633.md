# [H] XWiki Platform may show email addresses in clear in REST results

## Summary
Severity: High
Advisory: GHSA-8g9c-c9cm-9c56
CVE: CVE-2023-35151
CWE: CWE-359, CWE-668
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-06-20
Source: https://github.com/advisories/GHSA-8g9c-c9cm-9c56
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-rest-server` — affected >=7.3-milestone-1 <14.4.8
- Maven: `org.xwiki.platform:xwiki-platform-rest-server` — affected >=14.5 <14.10.6
- Maven: `org.xwiki.platform:xwiki-platform-rest-server` — affected >=15.0-rc-1 <15.1

## Details
### Impact
Any user can call a REST endpoint and obtain the obfuscated passwords (even when the mail obfuscation is activated).

For instance, by calling http://localhost:8080/xwiki/rest/wikis/xwiki/spaces/XWiki/pages/U1/objects/XWiki.XWikiUsers/0 when user `U1` exists on wiki `xwiki`.

### Patches
The issue has been patched on XWiki 14.4.8, 14.10.6, and 15.1 

### Workarounds
There is no known workaround. It is advised to upgrade to one of the patched versions.

### References
- https://jira.xwiki.org/browse/XWIKI-16138
- https://github.com/xwiki/xwiki-platform/commit/824cd742ecf5439971247da11bfe7e0ad2b10ede

### For more information

If you have any questions or comments about this advisory:
* Open an issue in [Jira XWiki.org](https://jira.xwiki.org/)
* Email us at [Security Mailing List](mailto:security@xwiki.org)

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-8g9c-c9cm-9c56
- https://nvd.nist.gov/vuln/detail/CVE-2023-35151
- https://github.com/xwiki/xwiki-platform/commit/824cd742ecf5439971247da11bfe7e0ad2b10ede
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-16138
