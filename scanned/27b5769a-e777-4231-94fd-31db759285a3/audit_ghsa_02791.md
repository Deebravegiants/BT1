# [M] Cross site scripting in froala-editor

## Summary
Severity: Medium
Advisory: GHSA-97x5-cc53-cv4v
CVE: CVE-2020-22864
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2021-10-28
Source: https://github.com/advisories/GHSA-97x5-cc53-cv4v
Type: github-advisory

## Affected
- npm: `froala-editor` — affected >=0 <4.0.11

## Details
A cross site scripting (XSS) vulnerability in the Insert Video function of Froala WYSIWYG Editor allows attackers to execute arbitrary web scripts or HTML.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-22864
- https://github.com/froala/wysiwyg-editor/issues/3880
- https://github.com/418sec/wysiwyg-editor/pull/1
- https://github.com/froala/wysiwyg-editor/pull/3911
- https://github.com/froala/wysiwyg-editor
- https://github.com/froala/wysiwyg-editor/releases/tag/v4.0.11
- https://www.youtube.com/watch?v=WE3b1iSnWJY
