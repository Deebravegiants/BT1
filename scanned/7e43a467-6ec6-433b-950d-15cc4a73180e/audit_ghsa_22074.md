# [C] Django Allows Redirect via Data URL

## Summary
Severity: Critical
Advisory: GHSA-78vx-ggch-wghm
CVE: CVE-2012-3442
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-78vx-ggch-wghm
Type: github-advisory

## Affected
- PyPI: `Django` — affected >=0 <1.3.2
- PyPI: `Django` — affected >=1.4 <1.4.1

## Details
The (1) `django.http.HttpResponseRedirect` and (2) `django.http.HttpResponsePermanentRedirect` classes in Django before 1.3.2 and 1.4.x before 1.4.1 do not validate the scheme of a redirect target, which might allow remote attackers to conduct cross-site scripting (XSS) attacks via a `data:` URL.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2012-3442
- https://github.com/django/django/commit/4dea4883e6c50d75f215a6b9bcbd95273f57c72d
- https://github.com/django/django/commit/e34685034b60be1112160e76091e5aee60149fa1
- https://github.com/django/django
- https://github.com/pypa/advisory-database/tree/main/vulns/django/PYSEC-2012-2.yaml
- https://www.djangoproject.com/weblog/2012/jul/30/security-releases-issued
- http://www.debian.org/security/2012/dsa-2529
- http://www.mandriva.com/security/advisories?name=MDVSA-2012:143
- http://www.openwall.com/lists/oss-security/2012/07/31/1
- http://www.openwall.com/lists/oss-security/2012/07/31/2
- http://www.ubuntu.com/usn/USN-1560-1
