# [M] Dolibarr ERP and CRM contain XSS Vulnerabilities

## Summary
Severity: Medium
Advisory: GHSA-jh5p-wpg2-8rgv
CVE: CVE-2016-1912
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-jh5p-wpg2-8rgv
Type: github-advisory

## Affected
- Packagist: `dolibarr/dolibarr` — affected >=0

## Details
Multiple cross-site scripting (XSS) vulnerabilities in Dolibarr ERP/CRM 3.8.3 allow remote authenticated users to inject arbitrary web script or HTML via the (1) lastname, (2) firstname, (3) email, (4) job, or (5) signature parameter to htdocs/user/card.php.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-1912
- https://github.com/Dolibarr/dolibarr/issues/4341
- https://github.com/GPCsolutions/dolibarr/commit/0d3181324c816bdf664ca5e1548dfe8eb05c54f8
- https://twitter.com/MickaelDorigny/status/684456187870457857
- http://packetstormsecurity.com/files/135201/Dolibarr-3.8.3-Cross-Site-Scripting.html
- http://www.information-security.fr/xss-dolibarr-version-3-8-3
