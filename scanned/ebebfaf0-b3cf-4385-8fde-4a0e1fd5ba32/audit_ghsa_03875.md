# [M] Cross-site scripting in Jupyter Notebook

## Summary
Severity: Medium
Advisory: GHSA-jqwc-jm56-wcwj
CVE: CVE-2018-21030
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2019-11-08
Source: https://github.com/advisories/GHSA-jqwc-jm56-wcwj
Type: github-advisory

## Affected
- PyPI: `notebook` — affected >=0 <5.5.0rc1

## Details
Jupyter Notebook before 5.5.0 does not use a CSP header to treat served files as belonging to a separate origin. Thus, for example, an XSS payload can be placed in an SVG document.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-21030
- https://github.com/jupyter/notebook/pull/3341
- https://github.com/jupyter/notebook/commit/e321c80776542b8d6f3411af16f9e21e51e27687
- https://github.com/advisories/GHSA-jqwc-jm56-wcwj
- https://github.com/jupyter/notebook
- https://github.com/jupyter/notebook/releases/tag/5.5.0
- https://github.com/pypa/advisory-database/tree/main/vulns/notebook/PYSEC-2019-157.yaml
- https://lists.debian.org/debian-lts-announce/2020/11/msg00033.html
