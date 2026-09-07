# [M] tablib: Stored XSS in the HTML export via unescaped dataset title

## Summary
Severity: Medium
Advisory: GHSA-gqgw-jghv-mxwx
CVE: CVE-2026-9318
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-08-12
Source: https://github.com/advisories/GHSA-gqgw-jghv-mxwx
Type: github-advisory

## Affected
- PyPI: `tablib` — affected >=0 <3.10.0

## Details
tablib prior to 3.10.0 contains a stored cross-site scripting vulnerability in the HTML export functionality that allows attackers to execute arbitrary JavaScript by embedding malicious payloads in dataset titles, which are interpolated unsanitized into HTML output via the export_book method in the _html.py format handler. Attackers can rename worksheet sheets in imported files such as XLSX, ODS, XLS, or YAML with script payloads that are assigned to the Dataset title attribute and rendered unescaped inside an HTML h3 tag, leading to session hijacking, unauthorized administrative actions, and sensitive data exposure when the output is rendered in a browser.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-9318
- https://github.com/jazzband/tablib/pull/668
- https://github.com/jazzband/tablib
- https://github.com/jazzband/tablib/releases/tag/v3.10.0
- https://www.vulncheck.com/advisories/tablib-versions-prior-to-stored-xss-via-html-export-dataset-title
