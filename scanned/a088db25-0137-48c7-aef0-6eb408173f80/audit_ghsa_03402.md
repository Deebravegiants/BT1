# [H] Cross-Site Request Forgery in Webargs

## Summary
Severity: High
Advisory: GHSA-fjq3-5pxw-4wj4
CVE: CVE-2020-7965
CWE: CWE-352
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-04-07
Source: https://github.com/advisories/GHSA-fjq3-5pxw-4wj4
Type: github-advisory

## Affected
- PyPI: `webargs` — affected >=5.0.0 <5.5.3
- PyPI: `webargs` — affected >=6.0.0b1 <6.0.0b4

## Details
flaskparser.py in Webargs 5.x through 5.5.2 doesn't check that the Content-Type header is application/json when receiving JSON input. If the request body is valid JSON, it will accept it even if the content type is application/x-www-form-urlencoded. This allows for JSON POST requests to be made across domains, leading to CSRF.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7965
- https://github.com/marshmallow-code/webargs/commit/b9ee8b0aa668207a363d9fd21d967eeadb975c3e
- https://github.com/marshmallow-code/webargs
- https://github.com/pypa/advisory-database/tree/main/vulns/webargs/PYSEC-2020-156.yaml
- https://webargs.readthedocs.io/en/latest/changelog.html
- https://webargs.readthedocs.io/en/latest/changelog.html#b4-2020-01-28
- https://webargs.readthedocs.io/en/latest/changelog.html#id11
