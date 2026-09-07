# [H] MantisBT: Stored XSS in print_all_bug_page_word.php

## Summary
Severity: High
Advisory: GHSA-h2wf-967x-gxvw
CVE: CVE-2026-62944
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:P/VC:H/VI:H/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-15
Source: https://github.com/advisories/GHSA-h2wf-967x-gxvw
Type: github-advisory

## Affected
- Packagist: `mantisbt/mantisbt` — affected >=0 <2.28.4

## Details
A missing output encoding call in print_all_bug_page_word.php allows any authenticated user to inject arbitrary HTML into an IMG tag's *alt* attribute via an image attachment with a crafted filename such as `probe." onload="alert(1)`. 

When any user views the HTML export page (print_all_bug_page_word.php?type_page=html&export=1), the rendered IMG tag becomes `<img src="..." alt="" onload="alert(1)" />`, breaking out of the alt attribute. 

### Impact
Cross-site scripting.

Impact is limited by MantisBT's Content Security Policy.

### Patches
- https://github.com/mantisbt/mantisbt/commit/bdd0e364f62759de272dfd4c89b4f51d27be9daa

### Workarounds
None

### Resources
- https://mantisbt.org/bugs/view.php?id=37234

### Credits
MantisBT thanks the [Dracosec Research Limited](https://dracosec.tech/) team (Chris Chan, Krecendo Hui, William Lam) for discovering and responsibly reporting the issue.

## References
- https://github.com/mantisbt/mantisbt/security/advisories/GHSA-h2wf-967x-gxvw
- https://github.com/mantisbt/mantisbt/commit/bdd0e364f62759de272dfd4c89b4f51d27be9daa
- https://github.com/mantisbt/mantisbt
- https://mantisbt.org/bugs/view.php?id=37234
