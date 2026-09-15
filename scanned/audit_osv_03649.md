# [H] ALPINE-CVE-2026-39863

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-39863
Ecosystem: Alpine:v3.14, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-04-08
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-39863
Type: osv

## Affected
- Alpine:v3.14: `kamailio` — affected >=6.0.0 <5.4.5-r2
- Alpine:v3.20: `kamailio` — affected >=6.0.0 <5.8.8-r0
- Alpine:v3.21: `kamailio` — affected >=6.0.0 <5.8.8-r0
- Alpine:v3.22: `kamailio` — affected >=6.0.0 <6.0.6-r0
- Alpine:v3.23: `kamailio` — affected >=6.0.0 <6.0.6-r0
- Alpine:v3.24: `kamailio` — affected >=6.0.0 <6.0.6-r0

## Details
Kamailio is an open source implementation of a SIP Signaling Server. Prior to 6.1.1, 6.0.6, and 5.8.8, an out-of-bounds access in the core of Kamailio (formerly OpenSER and SER) allows remote attackers to cause a denial of service (process crash) via a specially crafted data packet sent over TCP. The issue impacts Kamailio instances having TCP or TLS listeners. This vulnerability is fixed in 5.1.1, 6.0.6, and 5.8.8.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-39863
