# [M] ALPINE-CVE-2024-22020

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2024-22020
Ecosystem: Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.5 (CVSS:3.0/AV:L/AC:H/PR:N/UI:R/S:U/C:L/I:H/A:H)
Published: 2024-07-09
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-22020
Type: osv

## Affected
- Alpine:v3.19: `nodejs` — affected >=0 <20.15.1-r0
- Alpine:v3.20: `nodejs` — affected >=0 <20.15.1-r0
- Alpine:v3.21: `nodejs` — affected >=0 <20.15.1-r0
- Alpine:v3.22: `nodejs` — affected >=0 <20.15.1-r0
- Alpine:v3.23: `nodejs` — affected >=0 <20.15.1-r0
- Alpine:v3.24: `nodejs` — affected >=0 <20.15.1-r0

## Details
A security flaw in Node.js  allows a bypass of network import restrictions.
By embedding non-network imports in data URLs, an attacker can execute arbitrary code, compromising system security.
Verified on various platforms, the vulnerability is mitigated by forbidding data URLs in network imports.
Exploiting this flaw can violate network import security, posing a risk to developers and servers.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-22020
