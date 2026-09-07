# [M] messageformat prototype pollution vulnerability

## Summary
Severity: Medium
Advisory: GHSA-6xv4-9cqp-92rh
CVE: CVE-2025-57353
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2025-09-24
Source: https://github.com/advisories/GHSA-6xv4-9cqp-92rh
Type: github-advisory

## Affected
- npm: `@messageformat/runtime` — affected >=3.0.1 <3.0.2

## Details
The Runtime components of messageformat package for Node.js version 3.0.1 contain a prototype pollution vulnerability. Due to insufficient validation of nested message keys during the processing of message data, an attacker can manipulate the prototype chain of JavaScript objects by providing specially crafted input. This can result in the injection of arbitrary properties into the Object.prototype, potentially leading to denial of service conditions or unexpected application behavior. The vulnerability allows attackers to alter the prototype of base objects, impacting all subsequent object instances throughout the application's lifecycle. Version 3.0.2 contains a fix.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-57353
- https://github.com/messageformat/messageformat/issues/453
- https://github.com/messageformat/messageformat/issues/453#issuecomment-3466959449
- https://github.com/messageformat/messageformat/pull/464
- https://github.com/messageformat/messageformat/commit/82cd10b40e3f922f990bbcf88a6d14b70c0a3ce0
- https://github.com/VulnSageAgent/PoCs/tree/main/JavaScript/prototype-pollution/CVE-2025-57353
- https://github.com/messageformat/messageformat
