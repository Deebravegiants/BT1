# [M] Flask-Security vulnerable to Open Redirect

## Summary
Severity: Medium
Advisory: GHSA-cg8c-gc2j-2wf7
CVE: CVE-2021-23385
CWE: CWE-601
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-10-07
Source: https://github.com/advisories/GHSA-cg8c-gc2j-2wf7
Type: github-advisory

## Affected
- PyPI: `Flask-Security` — affected >=0

## Details
This affects all versions of package Flask-Security. When using the `get_post_logout_redirect` and `get_post_login_redirect` functions, it is possible to bypass URL validation and redirect a user to an arbitrary URL by providing multiple back slashes such as `\\\evil.com/path`. This vulnerability is only exploitable if an alternative WSGI server other than Werkzeug is used, or the default behaviour of Werkzeug is modified using `'autocorrect_location_header=False`.

**Note:** Flask-Security is not maintained anymore.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-23385
- https://github.com/mattupstate/flask-security
- https://security.snyk.io/vuln/SNYK-PYTHON-FLASKSECURITY-1293234
- https://snyk.io/blog/url-confusion-vulnerabilities
