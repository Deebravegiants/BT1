# [C] MrSwitch hello.js vulnerable to prototype pollution

## Summary
Severity: Critical
Advisory: GHSA-g3vf-47fv-8f3c
CVE: CVE-2021-26505
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-08-11
Source: https://github.com/advisories/GHSA-g3vf-47fv-8f3c
Type: github-advisory

## Affected
- npm: `hellojs` — affected >=0 <1.18.8

## Details
A prototype pollution vulnerability in MrSwitch hello.js prior to version 1.18.8 allows remote attackers to execute arbitrary code via `hello.utils.extend` function.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-26505
- https://github.com/MrSwitch/hello.js/issues/634
- https://github.com/MrSwitch/hello.js/commit/7ab50aeff2d41991f08d4ad6c0481125eea8f6b7
- https://github.com/MrSwitch/hello.js
