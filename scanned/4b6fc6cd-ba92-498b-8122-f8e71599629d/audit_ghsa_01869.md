# [M] Prototype pollution in paypal-adaptive

## Summary
Severity: Medium
Advisory: GHSA-v3r2-3fp4-rp46
CVE: CVE-2020-7643
CWE: CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:N/I:L/A:L (CVSS_V3)
Published: 2021-12-10
Source: https://github.com/advisories/GHSA-v3r2-3fp4-rp46
Type: github-advisory

## Affected
- npm: `paypal-adaptive` — affected >=0

## Details
paypal-adaptive through 0.4.2 manipulation of JavaScript objects resulting in Prototype Pollution. The PayPal function could be tricked into adding or modifying properties of Object.prototype using a `__proto__` payload.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7643
- https://github.com/Ideame/paypal-adaptive-sdk-nodejs
- https://github.com/Ideame/paypal-adaptive-sdk-nodejs/blob/master/lib/paypal-adaptive.js#L31
- https://snyk.io/vuln/SNYK-JS-PAYPALADAPTIVE-565089
