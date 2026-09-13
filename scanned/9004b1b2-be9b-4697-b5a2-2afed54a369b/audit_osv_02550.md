# [M] ALPINE-CVE-2022-30698

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2022-30698
Ecosystem: Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2022-08-01
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-30698
Type: osv

## Affected
- Alpine:v3.17: `unbound` — affected >=0 <1.16.2-r0
- Alpine:v3.18: `unbound` — affected >=0 <1.16.2-r0
- Alpine:v3.19: `unbound` — affected >=0 <1.16.2-r0
- Alpine:v3.20: `unbound` — affected >=0 <1.16.2-r0
- Alpine:v3.21: `unbound` — affected >=0 <1.16.2-r0
- Alpine:v3.22: `unbound` — affected >=0 <1.16.2-r0
- Alpine:v3.23: `unbound` — affected >=0 <1.16.2-r0
- Alpine:v3.24: `unbound` — affected >=0 <1.16.2-r0

## Details
NLnet Labs Unbound, up to and including version 1.16.1 is vulnerable to a novel type of the "ghost domain names" attack. The vulnerability works by targeting an Unbound instance. Unbound is queried for a subdomain of a rogue domain name. The rogue nameserver returns delegation information for the subdomain that updates Unbound's delegation cache. This action can be repeated before expiry of the delegation information by querying Unbound for a second level subdomain which the rogue nameserver provides new delegation information. Since Unbound is a child-centric resolver, the ever-updating child delegation information can keep a rogue domain name resolvable long after revocation. From version 1.16.2 on, Unbound checks the validity of parent delegation records before using cached delegation information.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-30698
