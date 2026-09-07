# [H] Django Allows Open Redirects

## Summary
Severity: High
Advisory: GHSA-vq3h-3q7v-9prw
CVE: CVE-2014-3730
CWE: CWE-20
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-vq3h-3q7v-9prw
Type: github-advisory

## Affected
- PyPI: `Django` — affected >=1.4 <1.4.13
- PyPI: `Django` — affected >=1.5 <1.5.8
- PyPI: `Django` — affected >=1.6 <1.6.5
- PyPI: `Django` — affected >=1.7a1 <1.7b4

## Details
The `django.util.http.is_safe_url` function in Django 1.4 before 1.4.13, 1.5 before 1.5.8, 1.6 before 1.6.5, and 1.7 before 1.7b4 does not properly validate URLs, which allows remote attackers to conduct open redirect attacks via a malformed URL, as demonstrated by "http:\\\djangoproject.com."

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-3730
- https://github.com/django/django/commit/601107524523bca02376a0ddc1a06c6fdb8f22f3
- https://github.com/django/django/commit/7feb54bbae3f637ab3c4dd4831d4385964f574df
- https://github.com/django/django/commit/ad32c218850ad40972dcef57beb460f8c979dd6d
- https://github.com/django/django
- https://github.com/pypa/advisory-database/tree/main/vulns/django/PYSEC-2014-20.yaml
- https://web.archive.org/web/20200228171223/http://www.securityfocus.com/bid/67410
- https://www.djangoproject.com/weblog/2014/may/14/security-releases-issued
- http://lists.opensuse.org/opensuse-updates/2014-09/msg00023.html
- http://secunia.com/advisories/61281
- http://ubuntu.com/usn/usn-2212-1
- http://www.debian.org/security/2014/dsa-2934
- http://www.openwall.com/lists/oss-security/2014/05/14/10
- http://www.openwall.com/lists/oss-security/2014/05/15/3
