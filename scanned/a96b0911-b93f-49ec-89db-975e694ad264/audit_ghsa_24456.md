# [H] Django Incorrectly Validates URLs

## Summary
Severity: High
Advisory: GHSA-f7cm-ccfp-3q4r
CVE: CVE-2014-0480
CWE: CWE-20
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-f7cm-ccfp-3q4r
Type: github-advisory

## Affected
- PyPI: `Django` — affected >=0 <1.4.14
- PyPI: `Django` — affected >=1.5 <1.5.9
- PyPI: `Django` — affected >=1.6 <1.6.6

## Details
The `core.urlresolvers.reverse` function in Django before 1.4.14, 1.5.x before 1.5.9, 1.6.x before 1.6.6, and 1.7 before release candidate 3 does not properly validate URLs, which allows remote attackers to conduct phishing attacks via a `//` (slash slash) in a URL, which triggers a scheme-relative URL to be generated.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-0480
- https://github.com/django/django/commit/45ac9d4fb087d21902469fc22643f5201d41a0cd
- https://github.com/django/django/commit/c2fe73133b62a1d9e8f7a6b43966570b14618d7e
- https://github.com/django/django/commit/da051da8df5e69944745072611351d4cfc6435d5
- https://github.com/django/django
- https://github.com/pypa/advisory-database/tree/main/vulns/django/PYSEC-2014-4.yaml
- https://web.archive.org/web/20140918034351/http://www.securityfocus.com/bid/69425
- https://www.djangoproject.com/weblog/2014/aug/20/security
- http://lists.opensuse.org/opensuse-updates/2014-09/msg00023.html
- http://www.debian.org/security/2014/dsa-3010
