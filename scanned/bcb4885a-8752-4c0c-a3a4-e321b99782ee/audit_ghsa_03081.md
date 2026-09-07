# [H] Insecure template handling in haml-coffee

## Summary
Severity: High
Advisory: GHSA-m7mf-vm62-7x3q
CVE: CVE-2021-32818
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2021-05-17
Source: https://github.com/advisories/GHSA-m7mf-vm62-7x3q
Type: github-advisory

## Affected
- npm: `haml-coffee` — affected >=0

## Details
haml-coffee is a JavaScript templating solution. haml-coffee mixes pure template data with engine configuration options through the Express render API. More specifically, haml-coffee supports overriding a series of HTML helper functions through its configuration options. A vulnerable application that passes user controlled request objects to the haml-coffee template engine may introduce RCE vulnerabilities. Additionally control over the escapeHtml parameter through template configuration pollution ensures that haml-coffee would not sanitize template inputs that may result in reflected Cross Site Scripting attacks against downstream applications. There is currently no fix for these issues as of the publication of this CVE. The latest version of haml-coffee is currently 1.14.1. For complete details refer to the referenced GHSL-2021-025.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-32818
- https://securitylab.github.com/advisories/GHSL-2021-025-haml-coffee
- https://www.npmjs.com/package/haml-coffee
