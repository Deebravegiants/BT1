# [C] django_make_app is vulnerable to Code Injection

## Summary
Severity: Critical
Advisory: GHSA-9pv8-q5rx-c8gq
CVE: CVE-2017-16764
CWE: CWE-94
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2018-07-13
Source: https://github.com/advisories/GHSA-9pv8-q5rx-c8gq
Type: github-advisory

## Affected
- PyPI: `django_make_app` — affected >=0

## Details
An exploitable vulnerability exists in the YAML parsing functionality in the `read_yaml_file` method in `io_utils.py` in django_make_app 0.1.3. A YAML parser can execute arbitrary Python commands resulting in command execution. An attacker can insert Python into loaded YAML to trigger this vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-16764
- https://github.com/illagrenan/django-make-app/issues/5
- https://github.com/illagrenan/django-make-app/commit/acd814433d1021aa8783362521b0bd151fdfc9d2
- https://github.com/advisories/GHSA-9pv8-q5rx-c8gq
- https://github.com/illagrenan/django-make-app
- https://github.com/pypa/advisory-database/tree/main/vulns/django-make-app/PYSEC-2017-79.yaml
- https://joel-malwarebenchmark.github.io/blog/2017/11/12/cve-2017-16764-vulnerability-in-django-make-app
