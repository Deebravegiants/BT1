# [H] Django Access Control Bypass possibly leading to SSRF, RFI, and LFI attacks 

## Summary
Severity: High
Advisory: GHSA-p99v-5w3c-jqq9
CVE: CVE-2021-33571
CWE: CWE-918
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2021-06-10
Source: https://github.com/advisories/GHSA-p99v-5w3c-jqq9
Type: github-advisory

## Affected
- PyPI: `Django` — affected >=2.2a1 <2.2.24
- PyPI: `Django` — affected >=3.0a1 <3.1.12
- PyPI: `Django` — affected >=3.2a1 <3.2.4

## Details
In Django 2.2 before 2.2.24, 3.x before 3.1.12, and 3.2 before 3.2.4, URLValidator, validate_ipv4_address, and validate_ipv46_address do not prohibit leading zero characters in octal literals. This may allow a bypass of access control that is based on IP addresses. (validate_ipv4_address and validate_ipv46_address are unaffected with Python 3.9.5+..) .

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-33571
- https://github.com/django/django/commit/203d4ab9ebcd72fc4d6eb7398e66ed9e474e118e
- https://github.com/django/django/commit/9f75e2e562fa0c0482f3dde6fc7399a9070b4a3d
- https://github.com/django/django/commit/f27c38ab5d90f68c9dd60cabef248a570c0be8fc
- https://docs.djangoproject.com/en/3.2/releases/security
- https://github.com/advisories/GHSA-p99v-5w3c-jqq9
- https://github.com/django/django
- https://github.com/pypa/advisory-database/tree/main/vulns/django/PYSEC-2021-99.yaml
- https://groups.google.com/g/django-announce/c/sPyjSKMi8Eo
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/B4SQG2EAF4WCI2SLRL6XRDJ3RPK3ZRDV
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/B4SQG2EAF4WCI2SLRL6XRDJ3RPK3ZRDV
- https://security.netapp.com/advisory/ntap-20210727-0004
- https://www.djangoproject.com/weblog/2021/jun/02/security-releases
