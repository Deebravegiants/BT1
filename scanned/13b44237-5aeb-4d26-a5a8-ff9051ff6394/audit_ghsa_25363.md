# [M] MantisBT XSS issue on the view_all_bug_page.php 

## Summary
Severity: Medium
Advisory: GHSA-4rrc-5vp6-m3f6
CVE: CVE-2020-16266
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-4rrc-5vp6-m3f6
Type: github-advisory

## Affected
- Packagist: `mantisbt/mantisbt` — affected >=2.1.0 <2.24.2

## Details
An XSS issue was discovered in MantisBT before 2.24.2. Improper escaping on view_all_bug_page.php allows a remote attacker to inject arbitrary HTML into the page by saving it into a text Custom Field, leading to possible code execution in the browser of any user subsequently viewing the issue (if CSP settings allow it).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-16266
- https://github.com/mantisbt/mantisbt/commit/9ef8f23a8119221d010251112b1255630a46d903
- https://github.com/mantisbt/mantisbt
- https://mantisbt.org/blog/archives/mantisbt/665
- https://mantisbt.org/bugs/view.php?id=27056
