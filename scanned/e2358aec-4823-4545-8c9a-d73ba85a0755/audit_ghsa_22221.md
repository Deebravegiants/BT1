# [M] Django settings leak in date template filter

## Summary
Severity: Medium
Advisory: GHSA-6wcr-wcqm-3mfh
CVE: CVE-2015-8213
CWE: CWE-200
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-6wcr-wcqm-3mfh
Type: github-advisory

## Affected
- PyPI: `Django` — affected >=1.7 <1.7.11
- PyPI: `Django` — affected >=1.8a1 <1.8.7
- PyPI: `Django` — affected >=1.9a1 <1.9rc2

## Details
The get_format function in `utils/formats.py` in Django before 1.7.x before 1.7.11, 1.8.x before 1.8.7, and 1.9.x before 1.9rc2 might allow remote attackers to obtain sensitive application secrets via a settings key in place of a date/time format setting, as demonstrated by `SECRET_KEY`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-8213
- https://github.com/django/django/commit/316bc3fc9437c5960c24baceb93c73f1939711e4
- https://github.com/django/django/commit/3ebbda0aef9e7a90ac6208bb8f9bc21228e2c7da
- https://github.com/django/django/commit/8a01c6b53169ee079cb21ac5919fdafcc8c5e172
- https://github.com/django/django/commit/9f83fc2f66f5a0bac7c291aec55df66050bb6991
- https://github.com/django/django
- https://github.com/pypa/advisory-database/tree/main/vulns/django/PYSEC-2015-11.yaml
- https://www.djangoproject.com/weblog/2015/nov/24/security-releases-issued
- http://lists.fedoraproject.org/pipermail/package-announce/2015-December/173375.html
- http://lists.fedoraproject.org/pipermail/package-announce/2015-December/174770.html
- http://lists.opensuse.org/opensuse-updates/2015-12/msg00014.html
- http://lists.opensuse.org/opensuse-updates/2015-12/msg00017.html
- http://rhn.redhat.com/errata/RHSA-2016-0129.html
- http://rhn.redhat.com/errata/RHSA-2016-0156.html
- http://rhn.redhat.com/errata/RHSA-2016-0157.html
- http://rhn.redhat.com/errata/RHSA-2016-0158.html
- http://www.debian.org/security/2015/dsa-3404
- http://www.securityfocus.com/bid/77750
- http://www.securitytracker.com/id/1034237
- http://www.ubuntu.com/usn/USN-2816-1
