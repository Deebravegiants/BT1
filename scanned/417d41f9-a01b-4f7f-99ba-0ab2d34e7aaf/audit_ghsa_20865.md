# [H] XWiki Platform Old Core vulnerable to Authentication Bypass Using the Login Action

## Summary
Severity: High
Advisory: GHSA-8h89-34w2-jpfm
CVE: CVE-2022-36092
CWE: CWE-287
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-09-16
Source: https://github.com/advisories/GHSA-8h89-34w2-jpfm
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-oldcore` — affected >=0 <13.10.4
- Maven: `org.xwiki.platform:xwiki-platform-oldcore` — affected >=14.0 <14.2

## Details
### Impact
All rights checks that would normally prevent a user from viewing a document on a wiki can be bypassed using the login action and directly specified templates. This exposes title, content and comments of any document and properties of objects (class and property name must be known, though). This is also exploitable on [private wikis](https://www.xwiki.org/xwiki/bin/view/Documentation/AdminGuide/Access%20Rights/#HPrivateWiki).

### Patches
This has been patched in versions 14.2 and 13.10.4 by properly checking view rights before loading documents and disallowing non-default templates in the login, registration and skin action.

### Workarounds
It would be possible to protect all templates individually by adding code to check access rights first, but due to the number of templates and the fact that some of them need to be used without view rights, this seems impractical.

### References
* https://jira.xwiki.org/browse/XWIKI-19549
* https://jira.xwiki.org/browse/XWIKI-18602

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [Jira XWiki.org](https://jira.xwiki.org/)
* Email us at [security mailing-list](mailto:security@xwiki.com)

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-8h89-34w2-jpfm
- https://nvd.nist.gov/vuln/detail/CVE-2022-36092
- https://github.com/xwiki/xwiki-platform/commit/71a6d0bb6f8ab718fcfaae0e9b8c16c2d69cd4bb
- https://github.com/xwiki/xwiki-platform/commit/9b7057d57a941592d763992d4299456300918208
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-18602
- https://jira.xwiki.org/browse/XWIKI-19549
