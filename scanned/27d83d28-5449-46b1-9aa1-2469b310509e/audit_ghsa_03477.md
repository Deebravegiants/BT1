# [H] OS Command Injection in curling

## Summary
Severity: High
Advisory: GHSA-xmxh-g7wj-8m4m
CVE: CVE-2019-10789
CWE: CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-04-13
Source: https://github.com/advisories/GHSA-xmxh-g7wj-8m4m
Type: github-advisory

## Affected
- npm: `curling` — affected >=0 <1.1.0

## Details
npm package `curling` before version 1.1.0 is vulnerable to Command Injection via the run function. The command argument can be controlled by users without any sanitization.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10789
- https://github.com/hgarcia/curling/blob/e861d625c074679a2931bcf4ce8da0afa8162c53/lib/curl-transport.js#L56
- https://snyk.io/vuln/SNYK-JS-CURLING-546484
