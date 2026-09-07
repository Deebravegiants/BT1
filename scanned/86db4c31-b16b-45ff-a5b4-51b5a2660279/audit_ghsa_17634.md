# [H] XWiki allows remote code execution through default value of wiki macro wiki-type parameters

## Summary
Severity: High
Advisory: GHSA-9875-cw22-f7cx
CVE: CVE-2025-49581
CWE: CWE-94
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-06-13
Source: https://github.com/advisories/GHSA-9875-cw22-f7cx
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-rendering-wikimacro-store` — affected >=11.10.11
- Maven: `org.xwiki.platform:xwiki-platform-rendering-wikimacro-store` — affected >=12.6.3
- Maven: `org.xwiki.platform:xwiki-platform-rendering-wikimacro-store` — affected >=12.8-rc-1 <16.4.7
- Maven: `org.xwiki.platform:xwiki-platform-rendering-wikimacro-store` — affected >=16.5.0-rc-1 <16.10.3
- Maven: `org.xwiki.platform:xwiki-platform-rendering-wikimacro-store` — affected >=17.0.0-rc-1 <17.0.0

## Details
### Impact
Any user with edit right on a page (could be the user's profile) can execute code (Groovy, Python, Velocity) with programming right by defining a wiki macro. This allows full access to the whole XWiki installation and thus impacts its confidentiality, integrity and availability. The main problem is that if a wiki macro parameter allows wiki syntax, its default value is executed with the rights of the author of the document where it is used. This can be exploited by overriding a macro like the `children` macro that is used in a page that has programming right like the page `XWiki.ChildrenMacro` and thus allows arbitrary script macros. The full reproduction steps can be found in the [original issue](https://jira.xwiki.org/browse/XWIKI-22760).

### Patches
This vulnerability has been patched in XWiki 16.4.7, 16.10.3 and 17.0.0 by executing wiki parameters with the rights of the wiki macro's author when the parameter's value is the default value.

### Workarounds
We're not aware of any workarounds except for upgrading.

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-9875-cw22-f7cx
- https://nvd.nist.gov/vuln/detail/CVE-2025-49581
- https://github.com/xwiki/xwiki-platform/commit/c99d501ed41cbee6a3c02ff927714531570789de
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-22760
