# [M] Django is vulnerable to DoS via XML serializer text extraction

## Summary
Severity: Medium
Advisory: GHSA-vrcr-9hj9-jcg6
CVE: CVE-2025-64460
CWE: CWE-407
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-12-02
Source: https://github.com/advisories/GHSA-vrcr-9hj9-jcg6
Type: github-advisory

## Affected
- PyPI: `Django` — affected >=5.2a1 <5.2.9
- PyPI: `Django` — affected >=5.1a1 <5.1.15
- PyPI: `Django` — affected >=4.2a1 <4.2.27

## Details
An issue was discovered in 5.2 before 5.2.9, 5.1 before 5.1.15, and 4.2 before 4.2.27.
Algorithmic complexity in `django.core.serializers.xml_serializer.getInnerText()` allows a remote attacker to cause a potential denial-of-service attack triggering CPU and memory exhaustion via specially crafted XML input processed by the XML `Deserializer`.
Earlier, unsupported Django series (such as 5.0.x, 4.1.x, and 3.2.x) were not evaluated and may also be affected.
Django would like to thank Seokchan Yoon for reporting this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-64460
- https://github.com/django/django/commit/0db9ea4669312f1f4973e09f4bca06ab9c1ec74b
- https://github.com/django/django/commit/1dbd07a608e495a0c229edaaf84d58d8976313b5
- https://github.com/django/django/commit/4d2b8803bebcdefd2b76e9e8fc528d5fddea93f0
- https://github.com/django/django/commit/99e7d22f55497278d0bcb2e15e72ef532e62a31d
- https://docs.djangoproject.com/en/dev/releases/security
- https://github.com/django/django
- https://github.com/pypa/advisory-database/tree/main/vulns/django/PYSEC-2025-109.yaml
- https://groups.google.com/g/django-announce
- https://www.djangoproject.com/weblog/2025/dec/02/security-releases
