# [C] Qwik vulnerable to Unauthenticated RCE via server$ Deserialization

## Summary
Severity: Critical
Advisory: GHSA-p9x5-jp3h-96mm
CVE: CVE-2026-27971
CWE: CWE-502
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-02
Source: https://github.com/advisories/GHSA-p9x5-jp3h-96mm
Type: github-advisory

## Affected
- npm: `@builder.io/qwik` — affected >=0 <1.19.1

## Details
### Summary
qwik <=1.19.0 is vulnerable to RCE due to an unsafe deserialization vulnerability in the `server$` RPC mechanism that allows any unauthenticated user to execute arbitrary code on the server with a single HTTP request. Affects any deployment where `require()` is available at runtime.

### Impact
- Remote Code Execution

## References
- https://github.com/QwikDev/qwik/security/advisories/GHSA-p9x5-jp3h-96mm
- https://nvd.nist.gov/vuln/detail/CVE-2026-27971
- https://github.com/QwikDev/qwik
- https://github.com/QwikDev/qwik/releases/tag/%40builder.io%2Fqwik%401.19.1
