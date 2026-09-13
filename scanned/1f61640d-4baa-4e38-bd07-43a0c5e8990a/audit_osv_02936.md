# [H] ALPINE-CVE-2023-50868

## Summary
Severity: High
Advisory: ALPINE-CVE-2023-50868
Ecosystem: Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-02-14
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-50868
Type: osv

## Affected
- Alpine:v3.16: `bind` — affected >=9.0.0 <9.16.48-r0
- Alpine:v3.17: `bind` — affected >=9.0.0 <9.18.24-r0
- Alpine:v3.18: `bind` — affected >=9.0.0 <9.18.24-r0
- Alpine:v3.19: `bind` — affected >=9.0.0 <9.18.24-r0
- Alpine:v3.20: `bind` — affected >=9.0.0 <9.18.24-r0
- Alpine:v3.21: `bind` — affected >=9.0.0 <9.18.24-r0
- Alpine:v3.22: `bind` — affected >=9.0.0 <9.18.24-r0
- Alpine:v3.23: `bind` — affected >=9.0.0 <9.18.24-r0
- Alpine:v3.24: `bind` — affected >=9.0.0 <9.18.24-r0
- Alpine:v3.17: `dnsmasq` — affected >=0 <2.90-r0
- Alpine:v3.18: `dnsmasq` — affected >=0 <2.90-r0
- Alpine:v3.19: `dnsmasq` — affected >=0 <2.90-r0
- Alpine:v3.20: `dnsmasq` — affected >=0 <2.90-r0
- Alpine:v3.21: `dnsmasq` — affected >=0 <2.90-r0
- Alpine:v3.22: `dnsmasq` — affected >=0 <2.90-r0
- Alpine:v3.23: `dnsmasq` — affected >=0 <2.90-r0
- Alpine:v3.24: `dnsmasq` — affected >=0 <2.90-r0
- Alpine:v3.17: `unbound` — affected >=0 <1.19.1-r0
- Alpine:v3.18: `unbound` — affected >=0 <1.19.1-r0
- Alpine:v3.19: `unbound` — affected >=0 <1.19.1-r0
- Alpine:v3.20: `unbound` — affected >=0 <1.19.1-r0
- Alpine:v3.21: `unbound` — affected >=0 <1.19.1-r0
- Alpine:v3.22: `unbound` — affected >=0 <1.19.1-r0
- Alpine:v3.23: `unbound` — affected >=0 <1.19.1-r0
- Alpine:v3.24: `unbound` — affected >=0 <1.19.1-r0

## Details
The Closest Encloser Proof aspect of the DNS protocol (in RFC 5155 when RFC 9276 guidance is skipped) allows remote attackers to cause a denial of service (CPU consumption for SHA-1 computations) via DNSSEC responses in a random subdomain attack, aka the "NSEC3" issue. The RFC 5155 specification implies that an algorithm must perform thousands of iterations of a hash function in certain situations.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-50868
