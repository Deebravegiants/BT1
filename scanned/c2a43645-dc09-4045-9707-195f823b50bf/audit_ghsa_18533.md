# [H] @nyariv/sandboxjs has Prototype Pollution vulnerability that may lead to RCE

## Summary
Severity: High
Advisory: GHSA-9qm3-6qrr-c76m
CVE: CVE-2025-34146
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-07-31
Source: https://github.com/advisories/GHSA-9qm3-6qrr-c76m
Type: github-advisory

## Affected
- npm: `@nyariv/sandboxjs` — affected >=0 <0.8.24

## Details
A prototype pollution vulnerability exists in @nyariv/sandboxjs versions <= 0.8.23, allowing attackers to inject arbitrary properties into Object.prototype via crafted JavaScript code. This can result in a denial-of-service (DoS) condition or, under certain conditions, escape the sandboxed environment intended to restrict code execution. The vulnerability stems from insufficient prototype access checks in the sandbox’s executor logic, particularly in the handling of JavaScript function objects returned.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-34146
- https://github.com/nyariv/SandboxJS/issues/31
- https://gist.github.com/Hagrid29/9df27829a491080f923c4f6b8518d7e3
- https://github.com/nyariv/SandboxJS
- https://www.npmjs.com/package/@nyariv/sandboxjs
- https://www.vulncheck.com/advisories/nyariv-sandboxjs-prototype-pollution-sandbox-escape-dos
