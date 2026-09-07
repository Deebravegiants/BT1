# [H] MantisBT has Stored HTML Injection/XSS when displaying Tags in Timeline

## Summary
Severity: High
Advisory: GHSA-73vx-49mv-v8w5
CVE: CVE-2026-33548
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-03-25
Source: https://github.com/advisories/GHSA-73vx-49mv-v8w5
Type: github-advisory

## Affected
- Packagist: `mantisbt/mantisbt` — affected >=2.28.0 <2.28.2

## Details
Improper escaping of tag names retrieved from History in Timeline (my_view_page.php) allows an attacker to inject HTML and, if CSP settings permit, achieve execution of arbitrary JavaScript, when displaying a tag that has been renamed or deleted.

### Impact
Cross-site scripting (XSS).

### Patches
f32787c14d4518476fe7f05f992dbfe6eaccd815

### Workarounds
* Edit offending History entries (using SQL)
* Wrap `$this->tag_name` in a string_html_specialchars() call in IssueTagTimelineEvent::html()

### Credits
MantisBT thanks Vishal Shukla for discovering and responsibly reporting the issue.

## References
- https://github.com/mantisbt/mantisbt/security/advisories/GHSA-73vx-49mv-v8w5
- https://nvd.nist.gov/vuln/detail/CVE-2026-33548
- https://github.com/mantisbt/mantisbt/commit/f32787c14d4518476fe7f05f992dbfe6eaccd815
- https://github.com/mantisbt/mantisbt
- https://mantisbt.org/bugs/view.php?id=36973
