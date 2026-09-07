# [M] Mistune: XSS via unescaped class option in Admonition directive

## Summary
Severity: Medium
Advisory: GHSA-g97x-gvcm-x72h
CVE: CVE-2026-59926
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:L/VI:L/VA:N/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2026-07-20
Source: https://github.com/advisories/GHSA-g97x-gvcm-x72h
Type: github-advisory

## Affected
- PyPI: `mistune` — affected >=0 <3.3.0

## Details
In `src/mistune/directives/admonition.py`, the `render_admonition()` function concatenates the `:class:` option directly into the HTML class attribute without escaping (lines 63-68).

This allows attribute injection and XSS even when `HTMLRenderer(escape=True)` is used.

The directive name parameter is safe (validated against whitelist), but the class option comes from raw user input.

## References
- https://github.com/lepture/mistune/security/advisories/GHSA-g97x-gvcm-x72h
- https://nvd.nist.gov/vuln/detail/CVE-2026-59926
- https://github.com/lepture/mistune/commit/a3cb6e5655308797e8be021d6c7b5bab13cbace2
- https://github.com/lepture/mistune
- https://github.com/lepture/mistune/releases/tag/v3.2.1
- https://github.com/pypa/advisory-database/tree/main/vulns/mistune/PYSEC-2026-2214.yaml
