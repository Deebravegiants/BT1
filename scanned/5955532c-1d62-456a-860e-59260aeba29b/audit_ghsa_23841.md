# [M] MantisBT vulnerable to XSS via unescaped output in browser_search_plugin.php

## Summary
Severity: Medium
Advisory: GHSA-wfg2-2wmw-6894
CVE: CVE-2022-28508
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-05
Source: https://github.com/advisories/GHSA-wfg2-2wmw-6894
Type: github-advisory

## Affected
- Packagist: `mantisbt/mantisbt` — affected >=0

## Details
An XSS issue was discovered in browser_search_plugin.php in MantisBT up to and including 2.25.2. Unescaped output of the return parameter allows an attacker to inject code into a hidden input field.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-28508
- https://github.com/YavuzSahbaz/CVE-2022-28508/blob/main/MantisBT%202.25.2%20XSS%20vulnurability
- https://github.com/mantisbt/mantisbt
- https://mantisbt.org
- https://sourceforge.net/projects/mantisbt
