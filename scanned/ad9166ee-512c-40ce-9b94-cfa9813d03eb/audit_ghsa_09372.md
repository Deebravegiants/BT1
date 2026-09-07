# [H] MantisBT has a Content Security Policy bypass via attachments

## Summary
Severity: High
Advisory: GHSA-9c3j-xm6v-j7j3
CVE: CVE-2026-40597
CWE: CWE-358, CWE-79
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:H/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-11
Source: https://github.com/advisories/GHSA-9c3j-xm6v-j7j3
Type: github-advisory

## Affected
- Packagist: `mantisbt/mantisbt` — affected >=0 <2.28.2

## Details
Given any pre-existing XSS / HTML injection vulnerability, an attacker can bypass the Content Security Policy's _script-src_ directive by uploading a crafted attachment to any issue that, when accessed via the _file_download.php_ link, will be downloaded with a valid JavaScript MIME type resulting in script execution.

The uploaded payload must be sniffed as a valid JavaScript MIME type by PHP finfo (see file_create_finfo() API function). Non-JavaScript MIME types will not get imported in a `<script>` tag by the browser, due to response header X-Content-Type-Options being set to _nosniff_, which requires all imported JavaScript files to be a valid JavaScript MIME type.

### Impact
Cross-site scripting

### Patches
- 9e3bee2e7b909f4e3596985892b8bc8bee9e0bfe

### Workarounds
None

### Credits
Thanks to siunam (Tang Cheuk Hei) for discovering and responsibly reporting the issue.

## References
- https://github.com/mantisbt/mantisbt/security/advisories/GHSA-9c3j-xm6v-j7j3
- https://nvd.nist.gov/vuln/detail/CVE-2026-40597
- https://github.com/mantisbt/mantisbt/commit/9e3bee2e7b909f4e3596985892b8bc8bee9e0bfe
- https://github.com/mantisbt/mantisbt
- https://mantisbt.org/bugs/view.php?id=37016
