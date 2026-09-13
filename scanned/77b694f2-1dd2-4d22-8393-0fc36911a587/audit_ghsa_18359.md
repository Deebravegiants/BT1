# [M] counterpart vulnerable to prototype pollution

## Summary
Severity: Medium
Advisory: GHSA-2488-w585-72ch
CVE: CVE-2025-57354
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:L (CVSS_V3)
Published: 2025-09-24
Source: https://github.com/advisories/GHSA-2488-w585-72ch
Type: github-advisory

## Affected
- npm: `counterpart` — affected >=0

## Details
A vulnerability exists in the `counterpart` library for Node.js and the browser due to insufficient sanitization of user-controlled input in translation key processing. The affected versions prior to 0.18.6 allow attackers to manipulate the library's translation functionality by supplying maliciously crafted keys containing prototype chain elements (e.g., __proto__ ), leading to prototype pollution. This weakness enables adversaries to inject arbitrary properties into the JavaScript Object prototype through the first parameter of the translate method when combined with specific separator configurations, potentially resulting in denial-of-service conditions or remote code execution in vulnerable applications. The issue arises from the library's failure to properly validate or neutralize special characters in translation key inputs before processing.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-57354
- https://github.com/martinandert/counterpart/issues/54
- https://github.com/VulnSageAgent/PoCs/tree/main/JavaScript/prototype-pollution/CVE-2025-57354
- https://github.com/martinandert/counterpart
