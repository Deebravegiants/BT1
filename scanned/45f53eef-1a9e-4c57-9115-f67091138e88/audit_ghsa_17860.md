# [H] XWiki exposes passwords and emails stored in fields not named password/email in xml.vm

## Summary
Severity: High
Advisory: GHSA-57q2-6cp4-9mq3
CVE: CVE-2025-54125
CWE: CWE-359
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-08-05
Source: https://github.com/advisories/GHSA-57q2-6cp4-9mq3
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-oldcore` — affected >=1.1 <16.4.7
- Maven: `org.xwiki.platform:xwiki-platform-oldcore` — affected >=16.5.0-rc-1 <16.10.5
- Maven: `org.xwiki.platform:xwiki-platform-oldcore` — affected >=17.0.0-rc-1 <17.2.0-rc-1
- Maven: `org.xwiki.platform:xwiki-platform-legacy-oldcore` — affected >=1.1 <16.4.7
- Maven: `org.xwiki.platform:xwiki-platform-legacy-oldcore` — affected >=16.5.0-rc-1 <16.10.5
- Maven: `org.xwiki.platform:xwiki-platform-legacy-oldcore` — affected >=17.0.0-rc-1 <17.2.0-rc-1

## Details
### Impact
The XML export of a page in XWiki that can be triggered by any user with view rights on a page by appending `?xpage=xml` to the URL includes password and email properties stored on a document that aren't named `password` or `email`. This allows any user to obtain the salted and hashed user account validation or password reset token. As those tokens are randomly generated strings, the immediate impact of this should be low. The user's password and email itself aren't exposed as those fields are named `password` and `email` and thus aren't affected. However, depending on how the wiki is used, there could be extensions or custom code that store passwords in plain text in such password properties that would be exposed by this vulnerability.

### Patches
This vulnerability has been fixed by completely removing the output of password and email fields in this XML export in versions 17.2.0 RC1, 16.10.5 and 16.4.7.

### Workarounds
If this XML export isn't needed, the file `templates/xml.vm` in the deployed WAR can be deleted. There isn't any feature in XWiki itself that depends on this XML export.

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-57q2-6cp4-9mq3
- https://nvd.nist.gov/vuln/detail/CVE-2025-54125
- https://github.com/xwiki/xwiki-platform/commit/742ee3482ef6c2bd4ad03d0de9cdd81d0e8f3d59
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-22810
