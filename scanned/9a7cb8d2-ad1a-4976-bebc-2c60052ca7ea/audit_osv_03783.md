# [H] ALPINE-CVE-2026-4892

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-4892
Ecosystem: Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-11
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-4892
Type: osv

## Affected
- Alpine:v3.22: `dnsmasq` — affected >=0 <2.91-r1
- Alpine:v3.23: `dnsmasq` — affected >=0 <2.91-r1
- Alpine:v3.24: `dnsmasq` — affected >=0 <2.92_p2-r0

## Details
A heap-based out-of-bounds write vulnerability in the DHCPv6 implementation of dnsmasq allows local attackers to execute arbitrary code with root privileges via a crafted DHCPv6 packet.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-4892
