# [H] XWiki leaks password hashes and other accessible password properties

## Summary
Severity: High
Advisory: GHSA-r38m-cgpg-qj69
CVE: CVE-2025-54124
CWE: CWE-359
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-08-05
Source: https://github.com/advisories/GHSA-r38m-cgpg-qj69
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-oldcore` — affected >=9.8-rc-1 <16.4.7
- Maven: `org.xwiki.platform:xwiki-platform-oldcore` — affected >=16.5.0-rc-1 <16.10.5
- Maven: `org.xwiki.platform:xwiki-platform-oldcore` — affected >=17.0.0-rc-1 <17.2.0-rc-1
- Maven: `org.xwiki.platform:xwiki-platform-legacy-oldcore` — affected >=9.8-rc-1 <16.4.7
- Maven: `org.xwiki.platform:xwiki-platform-legacy-oldcore` — affected >=16.5.0-rc-1 <16.10.5
- Maven: `org.xwiki.platform:xwiki-platform-legacy-oldcore` — affected >=17.0.0-rc-1 <17.2.0-rc-1

## Details
### Impact
Any user with edit right on a page of the wiki can create an XClass with a database list property that references a password property, for example the password hash that is stored for users. When adding an object of that XClass, the content of that password property is displayed. In practice, with a standard rights setup, this means that any user with an account on the wiki can access password hashes of all users, and possibly other password properties (with hashed or plain storage) that are on pages that the user can view.

### Patches
This vulnerability has been pached in XWiki 16.4.7, 16.10.5, and 17.2.0 by disallowing the use of password properties in database list properties. Additionally, queries for email properties are disallowed, too, when email obfuscation is enabled.

### Workarounds
We're not aware of any workarounds.

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-r38m-cgpg-qj69
- https://nvd.nist.gov/vuln/detail/CVE-2025-54124
- https://github.com/xwiki/xwiki-platform/commit/f2ca8649cba2ed3765061660bf5c7f801afa0b24
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-22811
