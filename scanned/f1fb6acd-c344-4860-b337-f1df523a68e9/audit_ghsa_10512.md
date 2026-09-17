# [M] Mafintosh's protocol-buffers-schema is vulnerable to prototype pollution

## Summary
Severity: Medium
Advisory: GHSA-j452-xhg8-qg39
CVE: CVE-2026-5758
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:L (CVSS_V3)
Published: 2026-04-15
Source: https://github.com/advisories/GHSA-j452-xhg8-qg39
Type: github-advisory

## Affected
- npm: `protocol-buffers-schema` — affected >=0 <3.6.1

## Details
JavaScript is vulnerable to prototype pollution in Mafintosh's protocol-buffers-schema Version 3.6.0, where an attacker may alter the application logic, bypass security checks, cause a DoS or achieve remote code execution.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-5758
- https://github.com/mafintosh/protocol-buffers-schema/pull/70
- https://github.com/mafintosh/protocol-buffers-schema
- https://morielharush.github.io/2026/04/12/cve-2026-5758-protocol-buffers-schema-prototype-pollution
