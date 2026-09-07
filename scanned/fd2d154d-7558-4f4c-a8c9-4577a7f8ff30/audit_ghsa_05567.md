# [M] XWiki Affected by Reflected Cross-Site Scripting (XSS) in Error Messages

## Summary
Severity: Medium
Advisory: GHSA-wvqx-m5px-6cmp
CVE: CVE-2026-24128
CWE: CWE-79, CWE-80
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:N/VI:N/VA:N/SC:H/SI:H/SA:H (CVSS_V4)
Published: 2026-01-23
Source: https://github.com/advisories/GHSA-wvqx-m5px-6cmp
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-web-templates` — affected >=7.0-milestone-2 <16.10.12
- Maven: `org.xwiki.platform:xwiki-platform-web-templates` — affected >=17.0.0-rc-1 <17.4.5
- Maven: `org.xwiki.platform:xwiki-platform-web-templates` — affected >=17.5.0-rc-1 <17.8.0-rc-1

## Details
### Impact
A reflected cross site scripting (XSS) vulnerability in XWiki allows an attacker to execute arbitrary actions in XWiki with the rights of the victim if the attacker manages to trick a victim into visiting a crafted URL. If the victim has administrative or programming rights, those rights can be exploited to gain full access to the XWiki installation.

### Patches
This vulnerability has been patched in XWiki 17.8.0RC1, 17.4.5 and 16.10.12.

### Workarounds
The [patch](https://github.com/xwiki/xwiki-platform/commit/8337ac8c3b19c37f306723b638b2cae8b0a57dbf#diff-8f16efedd19baae025db602d8736a105bfd8f72676af2c935b8195a0c356ee71) can be applied manually, only a single line in `templates/logging_macros.vm` needs to be changed, no restart is required.

### References
* https://github.com/xwiki/xwiki-platform/commit/8337ac8c3b19c37f306723b638b2cae8b0a57dbf
* https://jira.xwiki.org/browse/XWIKI-23462

### Attribution

We thank Mike Cole @mikecole-mg for discovering and reporting this vulnerability.

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-wvqx-m5px-6cmp
- https://nvd.nist.gov/vuln/detail/CVE-2026-24128
- https://github.com/xwiki/xwiki-platform/commit/8337ac8c3b19c37f306723b638b2cae8b0a57dbf
- https://github.com/xwiki/xwiki-platform/commit/8337ac8c3b19c37f306723b638b2cae8b0a57dbf#diff-8f16efedd19baae025db602d8736a105bfd8f72676af2c935b8195a0c356ee71
- https://github.com/xwiki/xwiki-platform
- https://github.com/xwiki/xwiki-platform/releases/tag/xwiki-platform-16.10.12
- https://github.com/xwiki/xwiki-platform/releases/tag/xwiki-platform-17.4.5
- https://github.com/xwiki/xwiki-platform/releases/tag/xwiki-platform-17.8.0-rc-1
- https://jira.xwiki.org/browse/XWIKI-23462
