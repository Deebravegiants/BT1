# [H] django-mfa2 vulnerable to MFA Replay attack

## Summary
Severity: High
Advisory: GHSA-vw39-2wj9-4q86
CVE: CVE-2022-42731
CWE: CWE-294
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-10-11
Source: https://github.com/advisories/GHSA-vw39-2wj9-4q86
Type: github-advisory

## Affected
- PyPI: `django-mfa2` — affected >=0 <2.5.1
- PyPI: `django-mfa2` — affected >=2.6.0 <2.6.1

## Details
mfa/FIDO2.py in django-mfa2 before 2.5.1 and 2.6.x before 2.6.1 allows a replay attack that could be used to register another device for a user. The device registration challenge is not invalidated after usage.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-42731
- https://github.com/mkalioby/django-mfa2/commit/54db5a513bcafa97a36e9f6dfa31d3c61fa8217b
- https://github.com/mkalioby/django-mfa2/commit/5fbb505e98ecdd409330a5c336ad5ec49631b0db
- https://github.com/mkalioby/django-mfa2
- https://github.com/mkalioby/django-mfa2/blob/0936ea253354dd95cb127f09d0efa31324caef27/mfa/FIDO2.py#L58
- https://github.com/mkalioby/django-mfa2/releases/tag/v2.5.1-release
- https://github.com/mkalioby/django-mfa2/releases/tag/v2.6.1-release
- https://github.com/pypa/advisory-database/tree/main/vulns/django-mfa2/PYSEC-2022-303.yaml
