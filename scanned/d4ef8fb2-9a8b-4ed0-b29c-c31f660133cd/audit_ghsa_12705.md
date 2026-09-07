# [M] Flask-AppBuilder vulnerable to possible disclosure of sensitive information on user error

## Summary
Severity: Medium
Advisory: GHSA-jhpr-j7cq-3jp3
CVE: CVE-2023-34110
CWE: CWE-209
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2023-06-22
Source: https://github.com/advisories/GHSA-jhpr-j7cq-3jp3
Type: github-advisory

## Affected
- PyPI: `Flask-AppBuilder` — affected >=0 <4.3.2

## Details
### Impact
An authenticated malicious actor with Admin privileges, could by adding a special character on the add, edit User forms trigger a database error, this error is surfaced back to this actor on the UI. On certain database engines this error can include the entire user row including the pbkdf2:sha256 hashed password.
 
### Patches
Fixed on 4.3.2

## References
- https://github.com/dpgaspar/Flask-AppBuilder/security/advisories/GHSA-jhpr-j7cq-3jp3
- https://nvd.nist.gov/vuln/detail/CVE-2023-34110
- https://github.com/dpgaspar/Flask-AppBuilder/pull/2045
- https://github.com/dpgaspar/Flask-AppBuilder/commit/ae25ad4c87a9051ebe4a4e8f02aee73232642626
- https://github.com/dpgaspar/Flask-AppBuilder
- https://github.com/dpgaspar/Flask-AppBuilder/releases/tag/v4.3.2
- https://github.com/pypa/advisory-database/tree/main/vulns/flask-appbuilder/PYSEC-2023-94.yaml
