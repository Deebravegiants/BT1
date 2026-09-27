# [M] Django Improper Output Neutralization for Logs vulnerability

## Summary
Severity: Medium
Advisory: GHSA-7xr5-9hcq-chf9
CVE: CVE-2025-48432
CWE: CWE-117
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:N/I:L/A:N (CVSS_V3)
Published: 2025-06-05
Source: https://github.com/advisories/GHSA-7xr5-9hcq-chf9
Type: github-advisory

## Affected
- PyPI: `Django` — affected >=5.2 <5.2.2
- PyPI: `Django` — affected >=5.0a1 <5.1.10
- PyPI: `Django` — affected >=0 <4.2.22

## Details
An issue was discovered in Django 5.2 before 5.2.2, 5.1 before 5.1.10, and 4.2 before 4.2.22. Internal HTTP response logging does not escape request.path, which allows remote attackers to potentially manipulate log output via crafted URLs. This may lead to log injection or forgery when logs are viewed in terminals or processed by external systems.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-48432
- https://docs.djangoproject.com/en/dev/releases/security
- https://github.com/django/django
- https://github.com/pypa/advisory-database/tree/main/vulns/django/PYSEC-2025-47.yaml
- https://groups.google.com/g/django-announce
- https://www.djangoproject.com/weblog/2025/jun/04/security-releases
- https://www.djangoproject.com/weblog/2025/jun/10/bugfix-releases
- http://www.openwall.com/lists/oss-security/2025/06/04/5
- http://www.openwall.com/lists/oss-security/2025/06/10/2
- http://www.openwall.com/lists/oss-security/2025/06/10/3
- http://www.openwall.com/lists/oss-security/2025/06/10/4
