# [C] Code Injection in Django

## Summary
Severity: Critical
Advisory: GHSA-rvq6-mrpv-m6rm
CVE: CVE-2014-0472
CWE: CWE-94
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-rvq6-mrpv-m6rm
Type: github-advisory

## Affected
- PyPI: `Django` — affected >=0 <1.4.11
- PyPI: `Django` — affected >=1.5 <1.5.6
- PyPI: `Django` — affected >=1.6 <1.6.3

## Details
The django.core.urlresolvers.reverse function in Django before 1.4.11, 1.5.x before 1.5.6, 1.6.x before 1.6.3, and 1.7.x before 1.7 beta 2 allows remote attackers to import and execute arbitrary Python modules by leveraging a view that constructs URLs using user input and a "dotted Python path."

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-0472
- https://github.com/django/django/commit/2a5bcb69f42b84464b24b5c835dca6467b6aa7f1
- https://github.com/django/django/commit/4352a50871e239ebcdf64eee6f0b88e714015c1b
- https://github.com/django/django/commit/c1a8c420fe4b27fb2caf5e46d23b5712fc0ac535
- https://github.com/django/django
- https://github.com/pypa/advisory-database/tree/main/vulns/django/PYSEC-2014-1.yaml
- https://www.djangoproject.com/weblog/2014/apr/21/security
- http://lists.opensuse.org/opensuse-updates/2014-09/msg00023.html
- http://rhn.redhat.com/errata/RHSA-2014-0456.html
- http://rhn.redhat.com/errata/RHSA-2014-0457.html
- http://www.debian.org/security/2014/dsa-2934
- http://www.ubuntu.com/usn/USN-2169-1
