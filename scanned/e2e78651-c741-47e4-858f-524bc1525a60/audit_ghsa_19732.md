# [H] XWiki uses the wrong wiki reference in AuthorizationManager

## Summary
Severity: High
Advisory: GHSA-gq32-758c-3wm3
CVE: CVE-2025-29924
CWE: CWE-269, CWE-863
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-03-19
Source: https://github.com/advisories/GHSA-gq32-758c-3wm3
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-security-authorization-api` — affected >=6.1-rc-1 <15.10.14
- Maven: `org.xwiki.platform:xwiki-platform-security-authorization-api` — affected >=16.0.0-rc-1 <16.4.6
- Maven: `org.xwiki.platform:xwiki-platform-security-authorization-api` — affected >=16.5.0-rc-1 <16.10.0-rc-1

## Details
### Impact

It's possible for an user to get access to private information through the REST API - but could also be through another API - when a sub wiki is using "Prevent unregistered users to view pages". The vulnerability only affects subwikis, and it only concerns specific right options such as "Prevent unregistered users to view pages". or "Prevent unregistered users to edit pages".

It's possible to detect the vulnerability by enabling "Prevent unregistered users to view pages" and then trying to access a page through the REST API without using any credentials.

### Patches

The vulnerability has been patched in XWiki 15.10.14, 16.4.6 and 16.10.0RC1. 

### Workarounds

There's no workaround.

### References

 * JIRA ticket: https://jira.xwiki.org/browse/XWIKI-22640
 * Commit of the fix: https://github.com/xwiki/xwiki-platform/commit/5f98bde87288326cf5787604e2bb87836875ed0e

### For more information

If you have any questions or comments about this advisory:
* Open an issue in [Jira XWiki.org](https://jira.xwiki.org/)
* Email us at [Security Mailing List](mailto:security@xwiki.org)

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-gq32-758c-3wm3
- https://nvd.nist.gov/vuln/detail/CVE-2025-29924
- https://github.com/xwiki/xwiki-platform/commit/5f98bde87288326cf5787604e2bb87836875ed0e
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-22640
