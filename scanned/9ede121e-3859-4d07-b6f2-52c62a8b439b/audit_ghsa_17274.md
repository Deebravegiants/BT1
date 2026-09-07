# [M] Vuetify has a Cross-site Scripting (XSS) vulnerability in the VDatePicker component

## Summary
Severity: Medium
Advisory: GHSA-9w3x-85mw-4fwm
CVE: CVE-2025-8082
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2025-12-12
Source: https://github.com/advisories/GHSA-9w3x-85mw-4fwm
Type: github-advisory

## Affected
- npm: `vuetify` — affected >=2.0.0 <3.0.0

## Details
Improper neutralization of the title date in the 'VDatePicker' component in Vuetify, allows unsanitized HTML to be inserted into the page. This can lead to a  Cross-Site Scripting (XSS) https://owasp.org/www-community/attacks/xss  attack. The vulnerability occurs because the 'title-date-format' property of the 'VDatePicker' can accept a user created function and assign its output to the 'innerHTML' property of the title element without sanitization.

This issue affects Vuetify versions greater than or equal to 2.0.0 and less than 3.0.0.

Note:
Version 2.x of Vuetify is End-of-Life and will not receive any updates to address this issue. For more information see  here https://v2.vuetifyjs.com/en/about/eol/ .

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-8082
- https://codepen.io/herodevs/pen/dPYGPyR/775285c0fd5a08038d4c85398815d644
- https://github.com/vuetifyjs/vuetify
- https://www.herodevs.com/vulnerability-directory/cve-2025-8082
