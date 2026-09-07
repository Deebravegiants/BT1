# [M] Mistune has XSS via unescaped figclass/figwidth in Figure directive

## Summary
Severity: Medium
Advisory: GHSA-58cw-g322-p94v
CVE: CVE-2026-44896
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-05-08
Source: https://github.com/advisories/GHSA-58cw-g322-p94v
Type: github-advisory

## Affected
- PyPI: `mistune` — affected >=0 <3.2.1

## Details
In `src/mistune/directives/image.py`, the `render_figure()` function concatenates `figclass` and `figwidth` options directly into HTML attributes without escaping (lines 152-168).

This allows attribute injection and XSS even when `HTMLRenderer(escape=True)` is used, because these values bypass the inline renderer.

Other attributes in the same file (src, alt, style) are properly escaped; figclass/figwidth were missed.

## References
- https://github.com/lepture/mistune/security/advisories/GHSA-58cw-g322-p94v
- https://nvd.nist.gov/vuln/detail/CVE-2026-44896
- https://github.com/lepture/mistune/commit/a3cb6e5655308797e8be021d6c7b5bab13cbace2
- https://github.com/lepture/mistune
- https://github.com/pypa/advisory-database/tree/main/vulns/mistune/PYSEC-2026-168.yaml
