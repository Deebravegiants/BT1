# [C] Melis Platform CMS SQL Injection

## Summary
Severity: Critical
Advisory: GHSA-mrmx-jfw8-qhgv
CVE: CVE-2025-10351
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-10-08
Source: https://github.com/advisories/GHSA-mrmx-jfw8-qhgv
Type: github-advisory

## Affected
- Packagist: `melisplatform/melis-cms` — affected >=0 <5.3.4

## Details
SQL injection vulnerability based on the melis-cms module of the Melis platform from Melis Technology. This vulnerability allows an attacker to retrieve, create, update, and delete databases through the 'idPage' parameter in the '/melis/MelisCms/PageEdition/getTinyTemplates' endpoint.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-10351
- https://github.com/melisplatform/melis-cms/commit/42d36326d9f6400b91db574483add2747af1db21
- https://github.com/ivansmc00/CVE-2025-10351-POC
- https://github.com/melisplatform/melis-cms
- https://www.incibe.es/en/incibe-cert/notices/aviso/multiple-vulnerabilities-melis-platform
