# [C] XSS in hello.js

## Summary
Severity: Critical
Advisory: GHSA-7jh9-6cpf-h4m7
CVE: CVE-2020-7741
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:L/A:H (CVSS_V3)
Published: 2021-01-13
Source: https://github.com/advisories/GHSA-7jh9-6cpf-h4m7
Type: github-advisory

## Affected
- npm: `hellojs` — affected >=0 <1.18.6

## Details
This affects the package hello.js before 1.18.6. The code get the param oauth_redirect from url and pass it to location.assign without any check and sanitisation. So we can simply pass some XSS payloads into the url param oauth_redirect, such as `javascript:alert(1)`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7741
- https://github.com/MrSwitch/hello.js/commit/d6f5137f30de6e0ef7048191ee6ae575fdc2f669
- https://github.com/MrSwitch/hello.js/blob/3b79ec93781b3d7b9c0b56f598e060301d1f3e73/dist/hello.all.js%23L1545
- https://snyk.io/vuln/SNYK-JS-HELLOJS-1014546
