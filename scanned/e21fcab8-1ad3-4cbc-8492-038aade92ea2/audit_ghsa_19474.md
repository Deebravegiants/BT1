# [C] org.xwiki.platform:xwiki-platform-security-requiredrights-default required rights analysis doesn't consider TextAreas with default content type

## Summary
Severity: Critical
Advisory: GHSA-mvgm-3rw2-7j4r
CVE: CVE-2025-32974
CWE: CWE-116, CWE-269
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2025-04-29
Source: https://github.com/advisories/GHSA-mvgm-3rw2-7j4r
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-security-requiredrights-default` — affected >=15.9-rc-1 <15.10.8
- Maven: `org.xwiki.platform:xwiki-platform-security-requiredrights-default` — affected >=16.0.0-rc-1 <16.2.0

## Details
### Impact
When editing a page, XWiki warns since version 15.9 when there is content on the page like a script macro that would gain more rights due to the editing. This analysis doesn't consider certain kinds of properties, allowing a user to put malicious scripts in there that will be executed after a user with script, admin, or programming rights edited the page. Such a malicious script could impact the confidentiality, integrity and availability of the whole XWiki installation.

To reproduce, as a user without script right, create a class with a `TextArea` property, create page with an object of that class and a Velocity macro in its content. Then, as an admin, try editing that page. Normally, there should be a warning but in vulnerable versions of XWiki, there is no warning.

### Patches
This vulnerability has been patched in XWiki 15.10.8 and 16.2.0.

### Workarounds
We're not aware of any workarounds apart from not editing pages that might have been edited by untrusted users as a user with script rights, e.g., by using separate user accounts for admin and non-admin tasks.

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-mvgm-3rw2-7j4r
- https://nvd.nist.gov/vuln/detail/CVE-2025-32974
- https://github.com/xwiki/xwiki-platform/commit/153dbfa2ef1a7a0a644fe3f889684c6a8738c5fc
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-22002
