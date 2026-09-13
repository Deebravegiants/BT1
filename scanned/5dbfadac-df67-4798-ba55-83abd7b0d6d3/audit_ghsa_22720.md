# [H] Django denial of service via file upload naming

## Summary
Severity: High
Advisory: GHSA-296w-6qhq-gf92
CVE: CVE-2014-0481
CWE: CWE-400
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-296w-6qhq-gf92
Type: github-advisory

## Affected
- PyPI: `Django` — affected >=0 <1.4.14
- PyPI: `Django` — affected >=1.5 <1.5.9
- PyPI: `Django` — affected >=1.6 <1.6.6

## Details
The default configuration for the file upload handling system in Django before 1.4.14, 1.5.x before 1.5.9, 1.6.x before 1.6.6, and 1.7 before release candidate 3 uses a sequential file name generation process when a file with a conflicting name is uploaded, which allows remote attackers to cause a denial of service (CPU consumption) by unloading a multiple files with the same name.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-0481
- https://github.com/django/django/commit/26cd48e166ac4d84317c8ee6d63ac52a87e8da99
- https://github.com/django/django/commit/30042d475bf084c6723c6217a21598d9247a9c41
- https://github.com/django/django/commit/dd0c3f4ee1a30c1a1e6055061c6ba6e58c6b54d1
- https://github.com/django/django
- https://github.com/pypa/advisory-database/tree/main/vulns/django/PYSEC-2014-5.yaml
- https://www.djangoproject.com/weblog/2014/aug/20/security
- http://lists.opensuse.org/opensuse-updates/2014-09/msg00023.html
- http://www.debian.org/security/2014/dsa-3010
