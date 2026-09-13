# [C] XWiki Platform vulnerable to remote code execution from account via SearchSuggestConfigSheet

## Summary
Severity: Critical
Advisory: GHSA-h63h-5c77-77p5
CVE: CVE-2024-37901
CWE: CWE-862, CWE-94, CWE-95
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2024-07-31
Source: https://github.com/advisories/GHSA-h63h-5c77-77p5
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-search-ui` — affected >=9.2-rc-1 <14.10.21
- Maven: `org.xwiki.platform:xwiki-platform-search-ui` — affected >=15.0-rc-1 <15.5.5
- Maven: `org.xwiki.platform:xwiki-platform-search-ui` — affected >=15.6-rc-1 <15.10.2

## Details
### Impact
Any user with edit right on any page can perform arbitrary remote code execution by adding instances of `XWiki.SearchSuggestConfig` and `XWiki.SearchSuggestSourceClass` to their user profile or any other page. This compromises the confidentiality, integrity and availability of the whole XWiki installation.

To reproduce on an instance, as a user without script nor programming rights, add an object of type `XWiki.SearchSuggestConfig` to your profile page, and an object of type `XWiki.SearchSuggestSourceClass` as well. On this last object, set both `name` and `icon` properties to `$services.logging.getLogger("attacker").error("I got programming: $services.security.authorization.hasAccess('programming')")` and `limit` and `engine` to `{{/html}}{{async}}{{velocity}}$services.logging.getLogger("attacker").error("I got programming: $services.security.authorization.hasAccess('programming')"){{/velocity}}{{/async}}`. Save and display the page. If the logs contain any message `ERROR attacker - I got programming: true` then the instance is vulnerable.

### Patches
This vulnerability has been patched in XWiki 14.10.21, 15.5.5 and 15.10.2.

### Workarounds
We're not aware of any workaround except upgrading.

### References
- https://jira.xwiki.org/browse/XWIKI-21473
- https://github.com/xwiki/xwiki-platform/commit/742cd4591642be4cdcaf68325f17540e0934e64e

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-h63h-5c77-77p5
- https://nvd.nist.gov/vuln/detail/CVE-2024-37901
- https://github.com/xwiki/xwiki-platform/commit/0b135760514fef73db748986a3311f3edd4a553b
- https://github.com/xwiki/xwiki-platform/commit/742cd4591642be4cdcaf68325f17540e0934e64e
- https://github.com/xwiki/xwiki-platform/commit/9ce3e0319869b6d8131fc4e0909736f7041566a4
- https://github.com/xwiki/xwiki-platform/commit/bbde8a4f564e3c28839440076334a9093e2b4834
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-21473
