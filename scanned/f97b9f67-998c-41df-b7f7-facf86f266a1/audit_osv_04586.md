# [H] BIT-django-2023-43665

## Summary
Severity: High
Advisory: BIT-django-2023-43665
Aliases: CVE-2023-43665, GHSA-h8gc-pgj2-vjm3, PYSEC-2023-226
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-django-2023-43665
Type: osv

## Affected
- Bitnami: `django` — affected >=4.2.0 <4.2.6

## Details
In Django 3.2 before 3.2.22, 4.1 before 4.1.12, and 4.2 before 4.2.6, the django.utils.text.Truncator chars() and words() methods (when used with html=True) are subject to a potential DoS (denial of service) attack via certain inputs with very long, potentially malformed HTML text. The chars() and words() methods are used to implement the truncatechars_html and truncatewords_html template filters, which are thus also vulnerable. NOTE: this issue exists because of an incomplete fix for CVE-2019-14232.

## References
- https://docs.djangoproject.com/en/4.2/releases/security/
- https://groups.google.com/forum/#%21forum/django-announce
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/HJFRPUHDYJHBH3KYHSPGULQM4JN7BMSU/
- https://security.netapp.com/advisory/ntap-20231221-0001/
- https://www.djangoproject.com/weblog/2023/oct/04/security-releases/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ZQJOMNRMVPCN5WMIZ7YSX5LQ7IR2NY4D/
- http://www.openwall.com/lists/oss-security/2024/03/04/1
- https://nvd.nist.gov/vuln/detail/CVE-2023-43665
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/ZQJOMNRMVPCN5WMIZ7YSX5LQ7IR2NY4D/
