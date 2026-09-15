# [M] Command injection in strapi

## Summary
Severity: Medium
Advisory: GHSA-xrjf-phvv-r4vr
CVE: CVE-2022-0764
CWE: CWE-77, CWE-78
Ecosystem: npm
CVSS: CVSS:3.0/AV:L/AC:L/PR:H/UI:R/S:U/C:H/I:H/A:L (CVSS_V3)
Published: 2022-02-27
Source: https://github.com/advisories/GHSA-xrjf-phvv-r4vr
Type: github-advisory

## Affected
- npm: `strapi` — affected >=0 <4.1.0

## Details
When creating a strapi app using npxcreate-strapi-app, we can inject arbitrary commands through the template cli argument as per the code in this particular [link](https://github.com/strapi/strapi/blob/master/packages/generators/app/lib/utils/fetch-npm-template.js#L13), this happens due to improper sanitization of user input.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-0764
- https://github.com/strapi/strapi/issues/12879
- https://github.com/strapi/strapi/commit/2a3f5e988be6a2c7dae5ac22b9e86d579b462f4c
- https://github.com/strapi/strapi
- https://github.com/strapi/strapi/blob/master/packages/generators/app/lib/utils/fetch-npm-template.js#L13
- https://huntr.dev/bounties/001d1c29-805a-4035-93bb-71a0e81da3e5
- https://www.github.com/strapi/strapi/commit/2a3f5e988be6a2c7dae5ac22b9e86d579b462f4c
