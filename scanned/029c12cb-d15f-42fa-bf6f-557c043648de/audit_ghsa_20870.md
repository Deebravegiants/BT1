# [M] XWiki Cross-Site Request Forgery (CSRF) for actions on tags

## Summary
Severity: Medium
Advisory: GHSA-fxwr-4vq9-9vhj
CVE: CVE-2022-36095
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-09-16
Source: https://github.com/advisories/GHSA-fxwr-4vq9-9vhj
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-web-templates` — affected >=2.0-milestone-1 <13.10.5
- Maven: `org.xwiki.platform:xwiki-platform-web-templates` — affected >=14.0 <14.3

## Details
### Impact
It's possible to perform a CSRF attack for adding or removing tags on XWiki pages. 

### Patches
The problem has been patched in XWiki 13.10.5 and 14.3. 

### Workarounds
It's possible to fix the issue without upgrading by locally modifying the documentTags.vm template in your filesystem, to apply the changes exposed there: https://github.com/xwiki/xwiki-platform/commit/7ca56e40cf79a468cea54d3480b6b403f259f9ae.

### References
https://jira.xwiki.org/browse/XWIKI-19550

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [Jira XWiki](https://jira.xwiki.org)
* Email us at [security ML](mailto:security@xwiki.org)

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-fxwr-4vq9-9vhj
- https://nvd.nist.gov/vuln/detail/CVE-2022-36095
- https://github.com/xwiki/xwiki-platform/commit/7ca56e40cf79a468cea54d3480b6b403f259f9ae
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-19550
