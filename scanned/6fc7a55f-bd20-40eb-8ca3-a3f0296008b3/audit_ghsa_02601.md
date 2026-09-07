# [H] Regular Expression Denial of Service in flask-restx

## Summary
Severity: High
Advisory: GHSA-3q6g-vf58-7m4g
CVE: CVE-2021-32838
CWE: CWE-1333, CWE-400
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-09-08
Source: https://github.com/advisories/GHSA-3q6g-vf58-7m4g
Type: github-advisory

## Affected
- PyPI: `flask-restx` — affected >=0 <0.5.1

## Details
Flask RESTX contains a regular expression that is vulnerable to [ReDoS](https://owasp.org/www-community/attacks/Regular_expression_Denial_of_Service_-_ReDoS) (Regular Expression Denial of Service) in `email_regex`.

## References
- https://github.com/python-restx/flask-restx/security/advisories/GHSA-3q6g-vf58-7m4g
- https://nvd.nist.gov/vuln/detail/CVE-2021-32838
- https://github.com/python-restx/flask-restx/issues/372
- https://github.com/python-restx/flask-restx/commit/bab31e085f355dd73858fd3715f7ed71849656da
- https://github.com/advisories/GHSA-3q6g-vf58-7m4g
- https://github.com/pypa/advisory-database/tree/main/vulns/flask-restx/PYSEC-2021-325.yaml
- https://github.com/python-restx/flask-restx
- https://github.com/python-restx/flask-restx/blob/fd99fe11a88531f5f3441a278f7020589f9d2cc0/flask_restx/inputs.py#L51
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/5UCTFVDU3677B5OBGK4EF5NMUPJLL6SQ
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/QUD6SWZLX52AAZUHDETJ2CDMQGEPGFL3
- https://pypi.org/project/flask-restx
