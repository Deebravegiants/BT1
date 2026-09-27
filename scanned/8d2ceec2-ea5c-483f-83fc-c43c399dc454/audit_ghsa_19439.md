# [C] org.xwiki.platform:xwiki-platform-component-wiki provides no warning when granting XWiki.ComponentClass programming right

## Summary
Severity: Critical
Advisory: GHSA-x7wv-5qg4-vmr6
CVE: CVE-2025-32973
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2025-04-29
Source: https://github.com/advisories/GHSA-x7wv-5qg4-vmr6
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-component-wiki` — affected >=15.9-rc-1 <15.10.12
- Maven: `org.xwiki.platform:xwiki-platform-component-wiki` — affected >=16.0.0-rc-1 <16.4.3
- Maven: `org.xwiki.platform:xwiki-platform-component-wiki` — affected >=16.5.0-rc-1 <16.8.0-rc-1

## Details
### Impact

When a user with programming right edits a document in XWiki that was last edited by a user without programming right and contains an `XWiki.ComponentClass`, there is no warning that this will grant programming right to this object. An attacker who created such a malicious object could use this to gain programming right on the wiki. For this, the attacker needs to have edit right on at least one page to place this object and then get an admin user to edit that document.

To reproduce the problem, as a user without programming right, add an object of type `XWiki.ComponentClass` to any page and then edit the page as a user with programming right. There should be warning displayed, if not, the XWiki installation is vulnerable.

While such a warning didn't exist in any version of XWiki, only in XWiki 15.9 RC1 these kinds of warnings have been introduced which is why this is considered the first version that has this vulnerability. Before that, the advice was to be careful when editing pages edited by untrusted users.

### Patches
This problem has been patched in XWiki 15.10.2, 16.4.3, and 16.8.0 RC1.

### Workarounds
We're not aware of any workarounds apart from not editing pages that might have been edited by untrusted users as a user with programming rights, e.g., by using separate user accounts for admin and non-admin tasks.

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-x7wv-5qg4-vmr6
- https://nvd.nist.gov/vuln/detail/CVE-2025-32973
- https://github.com/xwiki/xwiki-platform/commit/1a6f1b2e050770331c9a63d12a3fd8a36d199f62
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-22460
