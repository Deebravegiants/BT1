# [H] XWiki has no right protection on rollback action

## Summary
Severity: High
Advisory: GHSA-xh35-w7wg-95v3
CVE: CVE-2024-21648
CWE: CWE-274
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-01-08
Source: https://github.com/advisories/GHSA-xh35-w7wg-95v3
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-oldcore` — affected >=1.0 <14.10.17
- Maven: `org.xwiki.platform:xwiki-platform` — affected >=15.0-rc-1 <15.5.3
- Maven: `org.xwiki.platform:xwiki-platform` — affected >=15.6-rc-1 <15.8-rc-1

## Details
### Impact

The rollback action is missing a right protection: it means that a user can rollback to a previous version of the page to gain rights they don't have anymore. 
This vulnerability impacts all version of XWiki since rollback action is available. 

### Patches

The problem has been patched in XWiki 14.10.16, 15.5.3 and 15.8-rc-1 by ensuring that the rights are checked before performing the rollback. 

### Workarounds

There's no workaround for this vulnerability, except paying attention to delete old versions of documents that could allow users to gain more rights. 

### References

* JIRA ticket: https://jira.xwiki.org/browse/XWIKI-21257
* Commit: [4de72875ca49602796165412741033bfdbf1e680](https://github.com/xwiki/xwiki-platform/commit/4de72875ca49602796165412741033bfdbf1e680)

### For more information

If you have any questions or comments about this advisory:
* Open an issue in [Jira XWiki.org](https://jira.xwiki.org/)
* Email us at [Security Mailing List](mailto:security@xwiki.org)

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-xh35-w7wg-95v3
- https://nvd.nist.gov/vuln/detail/CVE-2024-21648
- https://github.com/xwiki/xwiki-platform/commit/1f3220f14bb3a4dcbd10d31134c39a06037f9a74
- https://github.com/xwiki/xwiki-platform/commit/4de72875ca49602796165412741033bfdbf1e680
- https://github.com/xwiki/xwiki-platform/commit/4fa7f302b14da6f05a6904a14e3741c4c06c40a1
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-21257
