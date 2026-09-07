# [M] Cross-site Scripting in Strapi

## Summary
Severity: Medium
Advisory: GHSA-mcqm-6ff4-53qx
CVE: CVE-2022-29894
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-06-14
Source: https://github.com/advisories/GHSA-mcqm-6ff4-53qx
Type: github-advisory

## Affected
- npm: `strapi` — affected >=0

## Details
Strapi v3.x.x versions and earlier contain a stored cross-site scripting vulnerability in file upload function. By exploiting this vulnerability, an arbitrary script may be executed on the web browser of the user who is logging in to the product with the administrative privilege.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-29894
- https://github.com/strapi/strapi
- https://jvn.jp/en/jp/JVN44550983/index.html
- https://strapi.io
