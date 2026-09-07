# [M] Django Improper Access Control

## Summary
Severity: Medium
Advisory: GHSA-mwv2-398h-v489
CVE: CVE-2007-0405
Ecosystem: PyPI
Published: 2022-05-01
Source: https://github.com/advisories/GHSA-mwv2-398h-v489
Type: github-advisory

## Affected
- PyPI: `Django` — affected >=0.95 <1.0

## Details
The LazyUser class in the AuthenticationMiddleware for Django 0.95 does not properly cache the user name across requests, which allows remote authenticated users to gain the privileges of a different user.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2007-0405
- https://github.com/django/django/commit/3c5782287e
- https://github.com/django/django/commit/e89f0a65581f82a5740bfe989136cea75d09cd67
- https://exchange.xforce.ibmcloud.com/vulnerabilities/31628
- https://github.com/django/django
- http://code.djangoproject.com/changeset/3754
