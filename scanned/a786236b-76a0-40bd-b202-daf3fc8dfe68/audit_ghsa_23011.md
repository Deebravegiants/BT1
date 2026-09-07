# [H] Django Access Restrictions Bypass 

## Summary
Severity: High
Advisory: GHSA-46x4-9jmv-jc8p
CVE: CVE-2016-2048
CWE: CWE-284
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:H/UI:N/S:U/C:L/I:H/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-46x4-9jmv-jc8p
Type: github-advisory

## Affected
- PyPI: `Django` — affected >=1.9 <1.9.2

## Details
Django 1.9.x before 1.9.2, when `ModelAdmin.save_as` is set to True, allows remote authenticated users to bypass intended access restrictions and create ModelAdmin objects via the "Save as New" option when editing objects and leveraging the "change" permission.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-2048
- https://github.com/django/django/commit/adbca5e4db42542575734b8e5d26961c8ada7265
- https://github.com/django/django
- https://github.com/pypa/advisory-database/tree/main/vulns/django/PYSEC-2016-14.yaml
- https://web.archive.org/web/20210123075529/http://www.securityfocus.com/bid/82329
- https://web.archive.org/web/20211204051406/http://www.securitytracker.com/id/1034894
- https://www.djangoproject.com/weblog/2016/feb/01/releases-192-and-189
