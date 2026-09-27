# [C] Command Injection in onion-oled-js

## Summary
Severity: Critical
Advisory: GHSA-rhwp-9vm9-547q
CVE: CVE-2021-23377
CWE: CWE-77
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-05-07
Source: https://github.com/advisories/GHSA-rhwp-9vm9-547q
Type: github-advisory

## Affected
- npm: `onion-oled-js` — affected >=0

## Details
This affects all versions up to and including version 0.0.2 of package onion-oled-js. If attacker-controlled user input is given to the scroll function, it is possible for an attacker to execute arbitrary commands. This is due to use of the child_process exec function without input sanitization.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-23377
- https://github.com/naddeoa/onion-oled-js
- https://github.com/naddeoa/onion-oled-js/blob/8a523645d2cc29130f98de661b742893773d760d/src/oled-exp.js#23L91
- https://snyk.io/vuln/SNYK-JS-ONIONOLEDJS-1078808
