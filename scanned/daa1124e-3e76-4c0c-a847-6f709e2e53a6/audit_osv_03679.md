# [H] ALPINE-CVE-2026-41292

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-41292
Ecosystem: Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-05-20
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-41292
Type: osv

## Affected
- Alpine:v3.24: `unbound` — affected >=0 <1.25.1-r0

## Details
NLnet Labs Unbound up to and including version 1.25.0 is vulnerable to a degradation of service attack related to parsing long lists of incoming EDNS options. An adversary sending queries with too many EDNS options can hold Unbound threads hostage while they are parsing and creating internal data structures for the options. Coordinated attacks can result in degradation and/or denial of service. Unbound 1.25.1 contains a patch with a fix to limit acceptable incoming EDNS options (100).

## References
- https://security.alpinelinux.org/vuln/CVE-2026-41292
