# [C] Zenario uses Twig filters insecurely in the Twig Snippet plugin

## Summary
Severity: Critical
Advisory: GHSA-hr2r-w6wc-25pv
CVE: CVE-2024-34461
CWE: CWE-94
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-05-04
Source: https://github.com/advisories/GHSA-hr2r-w6wc-25pv
Type: github-advisory

## Affected
- Packagist: `tribalsystems/zenario` — affected >=0 <9.5.60437

## Details
Zenario before 9.5.60437 uses Twig filters insecurely in the Twig Snippet plugin, and in the site-wide HEAD and BODY elements, enabling code execution by a designer or an administrator.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-34461
- https://github.com/TribalSystems/Zenario/commit/72afb59da34bace812bffb195d01168a357ff664
- https://github.com/TribalSystems/Zenario
- https://zenar.io/zenario-9/blog/zenario-9560437-patch-released
