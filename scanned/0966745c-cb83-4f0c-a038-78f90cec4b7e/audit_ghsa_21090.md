# [M] Whoogle Search Cross-site Scripting via string parameter

## Summary
Severity: Medium
Advisory: GHSA-mxvc-fwgx-j778
CVE: CVE-2022-25303
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2022-07-15
Source: https://github.com/advisories/GHSA-mxvc-fwgx-j778
Type: github-advisory

## Affected
- PyPI: `whoogle-search` — affected >=0 <0.7.2

## Details
The package whoogle-search before version 0.7.2 is vulnerable to Cross-site Scripting (XSS) via the query string parameter q. In the case where it does not contain the http string, it is used to build the error_message that is then rendered in the error.html template, using the [flask.render_template](https://flask.palletsprojects.com/en/2.1.x/api/flask.render_template) function. However, the error_message is rendered using the [| safe filter](https://jinja.palletsprojects.com/en/3.1.x/templates/working-with-automatic-escaping), meaning the user input is not escaped.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-25303
- https://github.com/benbusby/whoogle-search/commit/abc30d7da3b5c67be7ce84d4699f327442d44606
- https://github.com/advisories/GHSA-mxvc-fwgx-j778
- https://github.com/benbusby/whoogle-search
- https://github.com/benbusby/whoogle-search/blob/6d362ca5c7a00d2f691a2512461c5dfbfc01cbb3/app/routes.py%23L448
- https://github.com/pypa/advisory-database/tree/main/vulns/whoogle-search/PYSEC-2022-226.yaml
- https://snyk.io/vuln/SNYK-PYTHON-WHOOGLESEARCH-2803306
