# [M] XWiki has Reflected Cross-Site Scripting (XSS) in page history compare

## Summary
Severity: Medium
Advisory: GHSA-w4fj-87j5-f25c
CVE: CVE-2026-40105
CWE: CWE-80
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-04-14
Source: https://github.com/advisories/GHSA-w4fj-87j5-f25c
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-web-templates` — affected >=10.4-rc-1 <16.10.16
- Maven: `org.xwiki.platform:xwiki-platform-web-templates` — affected >=17.0.0-rc-1 <17.4.8
- Maven: `org.xwiki.platform:xwiki-platform-web-templates` — affected >=17.5.0-rc-1 <17.10.1

## Details
### Impact
A reflected cross-site scripting vulnerability (XSS) in the compare view between revisions of a page allows executing JavaScript code in the user's browser. If the current user is an admin, this can not only affect the current user but also the confidentiality, integrity and availability of the whole XWiki instance.

### Patches
The problem has been patched by properly escaping the URL parameters.

### Workarounds
The [patch](https://github.com/xwiki/xwiki-platform/commit/3c8a2ec985641367015c2db937574fcd360c788c#diff-a5e75a4e3820a63c02a32666dda67c73ee7885ab8e7f67e52cfcb3be5a13326e) can be applied manually to `templates/changesdoc.vm` in the deployed WAR.

### Attribution

XWiki thanks Mike Cole @mikecole-mg for discovering and reporting this vulnerability.

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-w4fj-87j5-f25c
- https://nvd.nist.gov/vuln/detail/CVE-2026-40105
- https://github.com/xwiki/xwiki-platform/commit/3c8a2ec985641367015c2db937574fcd360c788c
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-23472
