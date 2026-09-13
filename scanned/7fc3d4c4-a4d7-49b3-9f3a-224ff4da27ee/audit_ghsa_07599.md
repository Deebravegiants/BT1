# [C] Prototype Pollution via FormData Processing in Qwik City

## Summary
Severity: Critical
Advisory: GHSA-xqg6-98cw-gxhq
CVE: CVE-2026-25150
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:N/I:H/A:L (CVSS_V3)
Published: 2026-02-03
Source: https://github.com/advisories/GHSA-xqg6-98cw-gxhq
Type: github-advisory

## Affected
- npm: `@builder.io/qwik-city` — affected >=0 <1.19.0

## Details
### Summary

A Prototype Pollution vulnerability exists in the `formToObj()` function within `@builder.io/qwik-city` middleware. The function processes form field names with dot notation (e.g., `user.name`) to create nested objects, but fails to sanitize dangerous property names like `__proto__`, `constructor`, and `prototype`. This allows unauthenticated attackers to pollute `Object.prototype` by sending crafted HTTP POST requests, potentially leading to privilege escalation, authentication bypass, or denial of service.

### Impact
An unauthenticated attacker can supply specially crafted form field names that cause formToObj() to write dangerous keys (for example __proto__, constructor, prototype) into parsed objects. This results in Prototype Pollution of the server process and can cause privilege escalation, auth bypass, denial-of-service, or other global application integrity failures depending on how objects are used.

## References
- https://github.com/QwikDev/qwik/security/advisories/GHSA-xqg6-98cw-gxhq
- https://nvd.nist.gov/vuln/detail/CVE-2026-25150
- https://github.com/QwikDev/qwik/commit/5f65bae2bc33e6ca0c21e4cfcf9eae05077716f7
- https://github.com/QwikDev/qwik
