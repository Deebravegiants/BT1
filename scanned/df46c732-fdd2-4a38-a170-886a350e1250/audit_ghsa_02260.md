# [M] Open Redirect in Flask-User

## Summary
Severity: Medium
Advisory: GHSA-4298-89hc-6rfv
CVE: CVE-2021-23401
CWE: CWE-601
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2021-08-09
Source: https://github.com/advisories/GHSA-4298-89hc-6rfv
Type: github-advisory

## Affected
- PyPI: `Flask-User` — affected >=0

## Details
This affects all versions of package Flask-User. When using the `make_safe_url` function, it is possible to bypass URL validation and redirect a user to an arbitrary URL by providing multiple backslashes such as `/////evil.com/path` or `\\\evil.com/path`. This vulnerability is only exploitable if an alternative WSGI server other than Werkzeug is used, or the default behaviour of Werkzeug is modified using `autocorrect_location_header=False`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-23401
- https://github.com/advisories/GHSA-4298-89hc-6rfv
- https://github.com/lingthio/Flask-User
- https://github.com/lingthio/Flask-User/blob/master/flask_user/user_manager__utils.py
- https://github.com/pypa/advisory-database/tree/main/vulns/flask-user/PYSEC-2021-337.yaml
- https://snyk.io/vuln/SNYK-PYTHON-FLASKUSER-1293188
