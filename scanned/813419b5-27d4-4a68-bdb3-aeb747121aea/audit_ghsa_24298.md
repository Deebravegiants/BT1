# [M] Improper Input Validation in strapi

## Summary
Severity: Medium
Advisory: GHSA-65wv-528r-m892
CVE: CVE-2020-13961
CWE: CWE-20
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-65wv-528r-m892
Type: github-advisory

## Affected
- npm: `strapi` — affected >=0 <3.0.2

## Details
Strapi before 3.0.2 could allow a remote authenticated attacker to bypass security restrictions because templates are stored in a global variable without any sanitation. By sending a specially crafted request, an attacker could exploit this vulnerability to update the email template for both password reset and account confirmation emails.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-13961
- https://github.com/strapi/strapi/pull/6599
- https://exchange.xforce.ibmcloud.com/vulnerabilities/183045
- https://github.com/strapi/strapi
- https://github.com/strapi/strapi/releases/tag/v3.0.2
