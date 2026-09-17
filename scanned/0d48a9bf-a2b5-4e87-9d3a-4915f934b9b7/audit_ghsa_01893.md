# [M] Uncontrolled Resource Consumption in strapi

## Summary
Severity: Medium
Advisory: GHSA-23fp-fmrv-f5px
CVE: CVE-2020-8123
CWE: CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-12-10
Source: https://github.com/advisories/GHSA-23fp-fmrv-f5px
Type: github-advisory

## Affected
- npm: `strapi-admin` — affected >=0 <3.0.0-beta.18.4

## Details
A denial of service exists in strapi v3.0.0-beta.18.3 and earlier that can be abused in the admin console using admin rights can lead to arbitrary restart of the application.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-8123
- https://github.com/strapi/strapi/commit/c0c191c08f05fe10d7a6b1bf9475c1a651a89362
- https://hackerone.com/reports/768574
- https://github.com/strapi/strapi
