# [M] Django cross-site scripting (XSS) vulnerability via is_safe_url function 

## Summary
Severity: Medium
Advisory: GHSA-9cwg-mhxf-hh59
CVE: CVE-2013-6044
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-9cwg-mhxf-hh59
Type: github-advisory

## Affected
- PyPI: `Django` — affected >=1.4 <1.4.6
- PyPI: `Django` — affected >=1.5 <1.5.2

## Details
The is_safe_url function in utils/http.py in Django 1.4.x before 1.4.6, 1.5.x before 1.5.2, and 1.6 before beta 2 treats a URL's scheme as safe even if it is not HTTP or HTTPS, which might introduce cross-site scripting (XSS) or other vulnerabilities into Django applications that use this function, as demonstrated by "the login view in django.contrib.auth.views" and the javascript: scheme.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-6044
- https://github.com/django/django/commit/1a274ccd6bc1afbdac80344c9b6e5810c1162b5f
- https://github.com/django/django/commit/ae3535169af804352517b7fea94a42a1c9c4b762
- https://github.com/django/django/commit/ec67af0bd609c412b76eaa4cc89968a2a8e5ad6a
- https://exchange.xforce.ibmcloud.com/vulnerabilities/86437
- https://github.com/django/django
- https://github.com/pypa/advisory-database/tree/main/vulns/django/PYSEC-2013-21.yaml
- https://www.djangoproject.com/weblog/2013/aug/13/security-releases-issued
- http://lists.opensuse.org/opensuse-updates/2013-10/msg00015.html
- http://rhn.redhat.com/errata/RHSA-2013-1521.html
- http://seclists.org/oss-sec/2013/q3/369
- http://seclists.org/oss-sec/2013/q3/411
- http://www.debian.org/security/2013/dsa-2740
