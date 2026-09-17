# [C] Django Rest Framework jwt allows obtaining new token from notionally invalidated token

## Summary
Severity: Critical
Advisory: GHSA-fpjm-rp2g-3r4c
CVE: CVE-2020-10594
CWE: CWE-287
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2020-06-05
Source: https://github.com/advisories/GHSA-fpjm-rp2g-3r4c
Type: github-advisory

## Affected
- PyPI: `drf-jwt` — affected >=1.15.0 <1.15.1

## Details
An issue was discovered in drf-jwt 1.15.x before 1.15.1. It allows attackers with access to a notionally invalidated token to obtain a new, working token via the refresh endpoint, because the blacklist protection mechanism is incompatible with the token-refresh feature. NOTE: drf-jwt is a fork of jpadilla/django-rest-framework-jwt, which is unmaintained.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-10594
- https://github.com/Styria-Digital/django-rest-framework-jwt/issues/36
- https://github.com/jpadilla/django-rest-framework-jwt/issues/484
- https://github.com/Styria-Digital/django-rest-framework-jwt/commit/868b5c22ddad59772b447080183e7c7101bb18e0
- https://github.com/Styria-Digital/django-rest-framework-jwt
- https://github.com/advisories/GHSA-fpjm-rp2g-3r4c
- https://github.com/pypa/advisory-database/tree/main/vulns/drf-jwt/PYSEC-2020-40.yaml
- https://pypi.org/project/drf-jwt/1.15.1/#history
