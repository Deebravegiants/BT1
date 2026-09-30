# [M] FreeScout vulnerable to prototype pollution in getQueryParam

## Summary
Severity: Medium
Advisory: CVE-2026-53592
Aliases: GHSA-w5fc-8pp3-f755
CVSS: 4.6 (CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:U/C:L/I:L/A:L)
Published: 2026-07-20
Source: https://osv.dev/vulnerability/CVE-2026-53592
Type: osv

## Details
FreeScout is a free help desk and shared inbox built with PHP's Laravel framework. A Prototype Pollution condition in the `getQueryParam` function `/public/js/main.js` and was addressed in version 1.8.139 by blocking URL query keys matching the pattern `__proto__`. However, this mitigation is incomplete: it only filters top-level `__proto__` keys and fails to sanitize nested forms such as `b[__proto__][polluted]=PWNED`. As a result, an attacker-controlled URL query string can still write into `Object.prototype` on any page that loads `main.js`. Version 1.8.223 contains a updated fix.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53592.json
- https://github.com/freescout-help-desk/freescout/security/advisories/GHSA-w5fc-8pp3-f755
- https://nvd.nist.gov/vuln/detail/CVE-2026-53592
