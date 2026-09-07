# [M] django-allauth has an open redirect vulnerability

## Summary
Severity: Medium
Advisory: GHSA-2jpr-83rg-v67j
CVE: CVE-2026-27982
CWE: CWE-601
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2026-03-05
Source: https://github.com/advisories/GHSA-2jpr-83rg-v67j
Type: github-advisory

## Affected
- PyPI: `django-allauth` — affected >=0 <65.14.1

## Details
An open redirect vulnerability exists in django-allauth versions prior to 65.14.1 when SAML IdP initiated SSO is enabled (it is disabled by default), which may allow an attacker to redirect users to an arbitrary external website via a crafted URL.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-27982
- https://allauth.org/news/2026/02/django-allauth-65.14.1-released
- https://github.com/pennersr/django-allauth
- https://github.com/pypa/advisory-database/tree/main/vulns/django-allauth/PYSEC-2026-56.yaml
- https://jvn.jp/en/jp/JVN23669411
