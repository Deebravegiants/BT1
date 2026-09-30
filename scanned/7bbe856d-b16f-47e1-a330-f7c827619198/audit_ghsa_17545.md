# [H] XWiki makes title of inaccessible pages available through the class property values REST API

## Summary
Severity: High
Advisory: GHSA-mvp5-qx9c-c3fv
CVE: CVE-2025-49584
CWE: CWE-201
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-06-13
Source: https://github.com/advisories/GHSA-mvp5-qx9c-c3fv
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-rest-server` — affected >=10.9 <16.4.7
- Maven: `org.xwiki.platform:xwiki-platform-rest-server` — affected >=16.5.0-rc-1 <16.10.3
- Maven: `org.xwiki.platform:xwiki-platform-rest-server` — affected >=17.0.0-rc-1 <17.0.0

## Details
### Impact
The title of every single page whose reference is known can be accessed through the REST API as long as an XClass with a page property is accessible, this is the default for an XWiki installation. This allows an attacker to get titles of pages whose reference is known, one title per request. This doesn't affect fully [private wikis](https://www.xwiki.org/xwiki/bin/view/Documentation/AdminGuide/Access%20Rights/#HPrivateWiki) as the REST endpoint checks access rights on the XClass definition. The impact on confidentiality depends on the strategy for page names. By default, page names match the title, so the impact should be low but if page names are intentionally obfuscated because the titles are sensitive, the impact could be high.

### Patches
This has been fixed in XWiki 16.4.7, 16.10.3 and 17.0.0 by adding access control checks before getting the title of any page.

### Workarounds
We're not aware of any workarounds.

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-mvp5-qx9c-c3fv
- https://nvd.nist.gov/vuln/detail/CVE-2025-49584
- https://github.com/xwiki/xwiki-platform/commit/ee642f973a7c95d2d146fe03c81bcdee1871f4ec
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-22736
