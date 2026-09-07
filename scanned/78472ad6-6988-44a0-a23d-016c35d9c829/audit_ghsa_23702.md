# [M] Django cross-site scripting (XSS) vulnerability in the AdminURLFieldWidget widget

## Summary
Severity: Medium
Advisory: GHSA-4894-5vqc-6r2r
CVE: CVE-2013-4249
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-4894-5vqc-6r2r
Type: github-advisory

## Affected
- PyPI: `django` — affected >=1.5 <1.5.2

## Details
Cross-site scripting (XSS) vulnerability in the AdminURLFieldWidget widget in contrib/admin/widgets.py in Django 1.5.x before 1.5.2 and 1.6.x before 1.6 beta 2 allows remote attackers to inject arbitrary web script or HTML via a URLField.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-4249
- https://github.com/django/django/commit/90363e388c61874add3f3557ee654a996ec75d78
- https://github.com/django/django/commit/cbe6d5568f4f5053ed7228ca3c3d0cce77cf9560
- https://exchange.xforce.ibmcloud.com/vulnerabilities/86438
- https://github.com/django/django
- https://github.com/pypa/advisory-database/tree/main/vulns/django/PYSEC-2013-19.yaml
- https://web.archive.org/web/20201208180405/http://www.securitytracker.com/id/1028915
- https://www.djangoproject.com/weblog/2013/aug/13/security-releases-issued
- http://seclists.org/oss-sec/2013/q3/369
- http://seclists.org/oss-sec/2013/q3/411
