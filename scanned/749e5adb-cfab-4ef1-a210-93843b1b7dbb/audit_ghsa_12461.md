# [M] Solr search discloses email addresses of users

## Summary
Severity: Medium
Advisory: GHSA-2grh-gr37-2283
CVE: CVE-2023-50720
CWE: CWE-200
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2023-12-16
Source: https://github.com/advisories/GHSA-2grh-gr37-2283
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-search-solr-api` — affected >=0 <14.10.15
- Maven: `org.xwiki.platform:xwiki-platform-search-solr-api` — affected >=15.0-rc-1 <15.5.2
- Maven: `org.xwiki.platform:xwiki-platform-search-solr-api` — affected >=15.6-rc-1 <15.7-rc-1

## Details
### Impact
The Solr-based search in XWiki discloses the email addresses of users even when obfuscation of email addresses is enabled. To demonstrate the vulnerability, search for `objcontent:email*` using XWiki's regular search interface.

### Patches
This has been fixed in XWiki 14.10.15, 15.5.2 and 15.7RC1 by not indexing email address properties when obfuscation is enabled. Further, changing the setting now triggers re-indexing of the affected wiki(s).

### Workarounds
We're not aware of any workarounds.

### References
* https://jira.xwiki.org/browse/XWIKI-20371
* https://github.com/xwiki/xwiki-platform/commit/3e5272f2ef0dff06a8f4db10afd1949b2f9e6eea

### Attribution
This vulnerability was reported on Intigriti by [ynoof](https://twitter.com/ynoofAssiri) @Ynoof5.

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-2grh-gr37-2283
- https://nvd.nist.gov/vuln/detail/CVE-2023-50720
- https://github.com/xwiki/xwiki-platform/commit/3e5272f2ef0dff06a8f4db10afd1949b2f9e6eea
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-20371
