# [H] XWiki Platform's Livetable results still allow reconstructing password hashes using 768 requests

## Summary
Severity: High
Advisory: GHSA-rh28-mqj4-8x59
CVE: CVE-2026-48048
CWE: CWE-359
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-05-26
Source: https://github.com/advisories/GHSA-rh28-mqj4-8x59
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-livetable-ui` — affected >=6.2.1 <16.10.17
- Maven: `org.xwiki.platform:xwiki-platform-livetable-ui` — affected >=17.0.0-rc-1 <17.4.9
- Maven: `org.xwiki.platform:xwiki-platform-livetable-ui` — affected >=17.5.0-rc-1 <17.10.3

## Details
### Impact
XWiki discovered that the patch for GHSA-5cf8-vrr8-8hjm was insufficient and with slightly modified parameters to the `LiveTableResults`, it is still possible to discover password hashes one bit at a time, so with 768 requests, the full password salt and hash can be retrieved of a user.

### Patches
The check for password (and email properties) has been adjusted in XWiki 18.0.0RC1, 17.10.13, 17.4.9 and 16.10.17.

### Workarounds
The [patch](https://github.com/xwiki/xwiki-platform/commit/c4442716b02ffcdaa9d5e703b1db6203e36456fa#diff-5a739e5865b1f1ad9d79b724791be51b0095a0170cc078911c940478b13b949a) can be applied manually to the wiki page `XWiki.LiveTableResultsMacros`.

### Resources
* https://jira.xwiki.org/browse/XWIKI-23875
* https://github.com/xwiki/xwiki-platform/commit/c4442716b02ffcdaa9d5e703b1db6203e36456fa

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-rh28-mqj4-8x59
- https://github.com/xwiki/xwiki-platform/commit/c4442716b02ffcdaa9d5e703b1db6203e36456fa
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-23875
