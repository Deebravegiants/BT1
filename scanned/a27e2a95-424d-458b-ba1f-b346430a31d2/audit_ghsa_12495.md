# [H] Solr search discloses password hashes of all users

## Summary
Severity: High
Advisory: GHSA-p6cp-6r35-32mh
CVE: CVE-2023-50719
CWE: CWE-200, CWE-312
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-12-16
Source: https://github.com/advisories/GHSA-p6cp-6r35-32mh
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-search-solr-api` — affected >=7.2-milestone-2 <14.10.15
- Maven: `org.xwiki.platform:xwiki-platform-search-solr-api` — affected >=15.0-rc-1 <15.5.2
- Maven: `org.xwiki.platform:xwiki-platform-search-solr-api` — affected >=15.6-rc-1 <15.7-rc-1

## Details
### Impact
The Solr-based search in XWiki discloses the password hashes of all users to anyone with view right on the respective user profiles. By default, all user profiles are public. To reproduce, it is sufficient to search for `propertyvalue:?* AND reference:*.password` and then deselect the "Document" property under "Result type" in the "Refine your search" widget at the right of the search results. If this displays any passwords or password hashes, the installation is vulnerable.

By default, passwords in XWiki are salted and hashed with SHA-512. On XWiki versions affected by [CVE-2022-41933](https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-q2hm-2h45-v5g3), passwords are stored in plain text if they have been set using the password reset feature. This might affect XWiki installations that are using an external authentication mechanism such that passwords aren't stored in the wiki.

This vulnerability also affects any configurations used by extensions that contain passwords like API keys that are viewable for the attacker. Normally, such passwords aren't accessible but this vulnerability would disclose them as plain text.

### Patches
This has been patched in XWiki 14.10.15, 15.5.2 and 15.7RC1. This vulnerability has been patched as part of patching [GHSA-2grh-gr37-2283](https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-2grh-gr37-2283), the part of the fix that changes the indexing of single properties to use the same code as the main document for getting the property's value fixes this vulnerability.

### Workarounds
We're not aware of any workarounds apart from upgrading to a fixed version.

### References
* https://github.com/xwiki/xwiki-platform/commit/3e5272f2ef0dff06a8f4db10afd1949b2f9e6eea
* https://jira.xwiki.org/browse/XWIKI-21208

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-p6cp-6r35-32mh
- https://nvd.nist.gov/vuln/detail/CVE-2023-50719
- https://github.com/xwiki/xwiki-platform/commit/3e5272f2ef0dff06a8f4db10afd1949b2f9e6eea
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-21208
