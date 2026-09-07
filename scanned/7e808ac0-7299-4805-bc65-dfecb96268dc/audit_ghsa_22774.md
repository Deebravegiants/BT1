# [H] Django Might Allow CSRF Requests via URL Verification

## Summary
Severity: High
Advisory: GHSA-wxg3-mfph-qg9w
CVE: CVE-2011-4138
CWE: CWE-20
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-wxg3-mfph-qg9w
Type: github-advisory

## Affected
- PyPI: `Django` — affected >=0 <1.2.7
- PyPI: `Django` — affected >=1.3 <1.3.1

## Details
The `verify_exists` functionality in the URLField implementation in Django before 1.2.7 and 1.3.x before 1.3.1 originally tests a URL's validity through a HEAD request, but then uses a GET request for the new target URL in the case of a redirect, which might allow remote attackers to trigger arbitrary GET requests with an unintended source IP address via a crafted Location header.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2011-4138
- https://github.com/django/django/commit/1a76dbefdfc60e2d5954c0ba614c3d054ba9c3f0
- https://github.com/django/django/commit/7268f8af86186518821d775c530d5558fd726930
- https://bugzilla.redhat.com/show_bug.cgi?id=737366
- https://github.com/django/django
- https://github.com/pypa/advisory-database/tree/main/vulns/django/PYSEC-2011-3.yaml
- https://hermes.opensuse.org/messages/14700881
- https://www.djangoproject.com/weblog/2011/sep/09
- https://www.djangoproject.com/weblog/2011/sep/10/127
- http://openwall.com/lists/oss-security/2011/09/11/1
- http://openwall.com/lists/oss-security/2011/09/13/2
- http://www.debian.org/security/2011/dsa-2332
