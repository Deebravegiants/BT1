# [C] xwiki-platform-web-templates vulnerable to Eval Injection

## Summary
Severity: Critical
Advisory: GHSA-hg5x-3w3x-7g96
CVE: CVE-2023-29512
CWE: CWE-74
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:L (CVSS_V3)
Published: 2023-04-20
Source: https://github.com/advisories/GHSA-hg5x-3w3x-7g96
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-web-templates` — affected >=1.0B1 <13.10.11
- Maven: `org.xwiki.platform:xwiki-platform-web-templates` — affected >=14.0-rc-1 <14.4.8
- Maven: `org.xwiki.platform:xwiki-platform-web-templates` — affected >=14.5 <14.10.1

## Details
### Impact
Any user with edit rights on a page (e.g., it's own user page), can execute arbitrary Groovy, Python or Velocity code in XWiki leading to full access to the XWiki installation. The root cause is improper escaping of the information loaded from attachments in `imported.vm`, `importinline.vm`, and `packagelist.vm`. This page is installed by default.

Reproduction steps are described in https://jira.xwiki.org/browse/XWIKI-20267

### Patches
The vulnerability has been patched in XWiki 15.0-rc-1, 14.10.1, 14.4.8, and 13.10.11.

### Workarounds
The issue can be fixed by applying this [patch](https://github.com/xwiki/xwiki-platform/commit/e4bbdc23fea0be4ef1921d1a58648028ce753344) on `imported.vm`, `importinline.vm`, and `packagelist.vm`.

### References
- https://github.com/xwiki/xwiki-platform/commit/e4bbdc23fea0be4ef1921d1a58648028ce753344
- https://jira.xwiki.org/browse/XWIKI-20267


### For more information

If you have any questions or comments about this advisory:

*    Open an issue in [Jira XWiki.org](https://jira.xwiki.org/)
*    Email us at [Security Mailing List](mailto:security@xwiki.org)

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-hg5x-3w3x-7g96
- https://nvd.nist.gov/vuln/detail/CVE-2023-29512
- https://github.com/xwiki/xwiki-platform/commit/e4bbdc23fea0be4ef1921d1a58648028ce753344
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-20267
