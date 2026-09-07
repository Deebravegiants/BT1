# [M] Unauthenticated user can list hidden document from multiple velocity templates in XWiki

## Summary
Severity: Medium
Advisory: GHSA-qpp2-2mcp-2wm5
CVE: CVE-2022-24820
CWE: CWE-200, CWE-306, CWE-359
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-04-08
Source: https://github.com/advisories/GHSA-qpp2-2mcp-2wm5
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-web` — affected >=0 <12.10.11
- Maven: `org.xwiki.platform:xwiki-platform-web` — affected >=13.0.0 <13.4.4
- Maven: `org.xwiki.platform:xwiki-platform-web` — affected >=13.5.0 <13.9

## Details
### Impact
A guest user without the right to view pages of the wiki can still list documents by rendering some velocity documents.

### Patches
The problem has been patched in XWiki versions 12.10.11, 13.4.4, and 13.9-rc-1.

### Workarounds
There is no known workaround for this problem.

### References
https://jira.xwiki.org/browse/XWIKI-16544

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [Jira XWiki](https://jira.xwiki.org)
* Email us at [our security mailing list](mailto:security@xwiki.org)

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-qpp2-2mcp-2wm5
- https://nvd.nist.gov/vuln/detail/CVE-2022-24820
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-16544
