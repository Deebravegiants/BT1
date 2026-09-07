# [M] Django has an Improper Handling of Length Parameter Inconsistency

## Summary
Severity: Medium
Advisory: GHSA-w26r-rmm8-9c29
CVE: CVE-2026-5766
CWE: CWE-130
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-05-05
Source: https://github.com/advisories/GHSA-w26r-rmm8-9c29
Type: github-advisory

## Affected
- PyPI: `Django` — affected >=6.0 <6.0.5
- PyPI: `Django` — affected >=5.2 <5.2.14

## Details
An issue was discovered in 6.0 before 6.0.5 and 5.2 before 5.2.14. ASGI requests with a missing or understated `Content-Length` header can bypass the `FILE_UPLOAD_MAX_MEMORY_SIZE` limit, potentially loading large files into memory and causing service degradation.
 
As a reminder, Django expects a limit to be configured at the web server level rather than solely relying on `FILE_UPLOAD_MAX_MEMORY_SIZE`. Earlier, unsupported Django series (such as 5.0.x, 4.1.x, and 3.2.x) were not evaluated and may also be affected.

Django thanks Kyle Agronick for reporting this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-5766
- https://docs.djangoproject.com/en/dev/releases/security
- https://github.com/django/django
- https://github.com/pypa/advisory-database/tree/main/vulns/django/PYSEC-2026-54.yaml
- https://groups.google.com/g/django-announce
- https://www.djangoproject.com/weblog/2026/may/05/security-releases
