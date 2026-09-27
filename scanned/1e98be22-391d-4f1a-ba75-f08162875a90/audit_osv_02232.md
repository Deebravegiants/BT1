# [M] ALPINE-CVE-2021-3448

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2021-3448
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 4.0 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:N/I:L/A:N)
Published: 2021-04-08
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-3448
Type: osv

## Affected
- Alpine:v3.10: `dnsmasq` — affected >=0 <2.85-r0
- Alpine:v3.11: `dnsmasq` — affected >=0 <2.85-r0
- Alpine:v3.12: `dnsmasq` — affected >=0 <2.85-r0
- Alpine:v3.13: `dnsmasq` — affected >=0 <2.85-r0
- Alpine:v3.14: `dnsmasq` — affected >=0 <2.85-r0
- Alpine:v3.15: `dnsmasq` — affected >=0 <2.85-r0
- Alpine:v3.16: `dnsmasq` — affected >=0 <2.85-r0
- Alpine:v3.17: `dnsmasq` — affected >=0 <2.85-r0
- Alpine:v3.18: `dnsmasq` — affected >=0 <2.85-r0
- Alpine:v3.19: `dnsmasq` — affected >=0 <2.85-r0
- Alpine:v3.20: `dnsmasq` — affected >=0 <2.85-r0
- Alpine:v3.21: `dnsmasq` — affected >=0 <2.85-r0
- Alpine:v3.22: `dnsmasq` — affected >=0 <2.85-r0
- Alpine:v3.23: `dnsmasq` — affected >=0 <2.85-r0
- Alpine:v3.24: `dnsmasq` — affected >=0 <2.85-r0

## Details
A flaw was found in dnsmasq in versions before 2.85. When configured to use a specific server for a given network interface, dnsmasq uses a fixed port while forwarding queries. An attacker on the network, able to find the outgoing port used by dnsmasq, only needs to guess the random transmission ID to forge a reply and get it accepted by dnsmasq. This flaw makes a DNS Cache Poisoning attack much easier. The highest threat from this vulnerability is to data integrity.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-3448
