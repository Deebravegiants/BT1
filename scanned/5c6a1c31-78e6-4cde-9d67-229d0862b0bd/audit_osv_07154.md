# [M] BIT-node-2024-22020

## Summary
Severity: Medium
Advisory: BIT-node-2024-22020
Aliases: BIT-node-min-2024-22020, CVE-2024-22020
Ecosystem: Bitnami
Published: 2024-07-11
Source: https://osv.dev/vulnerability/BIT-node-2024-22020
Type: osv

## Affected
- Bitnami: `node` — affected >=21.0.0 <22.4.1

## Details
A security flaw in Node.js  allows a bypass of network import restrictions.
By embedding non-network imports in data URLs, an attacker can execute arbitrary code, compromising system security.
Verified on various platforms, the vulnerability is mitigated by forbidding data URLs in network imports.
Exploiting this flaw can violate network import security, posing a risk to developers and servers.

## References
- https://hackerone.com/reports/2092749
- http://www.openwall.com/lists/oss-security/2024/07/11/6
- http://www.openwall.com/lists/oss-security/2024/07/19/3
- https://security.netapp.com/advisory/ntap-20241122-0006/
- https://nvd.nist.gov/vuln/detail/CVE-2024-22020
- https://github.com/nodejs/node/releases/tag/v18.20.4
- https://github.com/nodejs/node/releases/tag/v20.15.1
- https://github.com/nodejs/node/releases/tag/v22.4.1
