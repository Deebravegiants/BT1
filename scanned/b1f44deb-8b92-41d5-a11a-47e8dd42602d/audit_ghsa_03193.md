# [C] Authorization bypass in Strapi

## Summary
Severity: Critical
Advisory: GHSA-7frv-9phw-vrvr
CVE: CVE-2020-27664
CWE: CWE-862
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-05-10
Source: https://github.com/advisories/GHSA-7frv-9phw-vrvr
Type: github-advisory

## Affected
- npm: `strapi` — affected >=0 <3.2.5

## Details
`admin/src/containers/InputModalStepperProvider/index.js` in Strapi before 3.2.5 has unwanted `/proxy?url=` functionality.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-27664
- https://github.com/strapi/strapi/pull/8442
- https://github.com/strapi/strapi/releases/tag/v3.2.5
