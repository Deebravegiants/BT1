# [H] ALPINE-CVE-2021-40114

## Summary
Severity: High
Advisory: ALPINE-CVE-2021-40114
Ecosystem: Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-10-27
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-40114
Type: osv

## Affected
- Alpine:v3.15: `snort` — affected >=2.0.0 <2.9.18-r0
- Alpine:v3.16: `snort` — affected >=2.0.0 <2.9.18-r0
- Alpine:v3.17: `snort` — affected >=2.0.0 <2.9.18-r0
- Alpine:v3.18: `snort` — affected >=2.0.0 <2.9.18-r0
- Alpine:v3.19: `snort` — affected >=2.0.0 <2.9.18-r0
- Alpine:v3.20: `snort` — affected >=2.0.0 <2.9.18-r0
- Alpine:v3.21: `snort` — affected >=2.0.0 <2.9.18-r0
- Alpine:v3.22: `snort` — affected >=2.0.0 <2.9.18-r0
- Alpine:v3.23: `snort` — affected >=2.0.0 <2.9.18-r0
- Alpine:v3.24: `snort` — affected >=2.0.0 <2.9.18-r0

## Details
Multiple Cisco products are affected by a vulnerability in the way the Snort detection engine processes ICMP traffic that could allow an unauthenticated, remote attacker to cause a denial of service (DoS) condition on an affected device. The vulnerability is due to improper memory resource management while the Snort detection engine is processing ICMP packets. An attacker could exploit this vulnerability by sending a series of ICMP packets through an affected device. A successful exploit could allow the attacker to exhaust resources on the affected device, causing the device to reload.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-40114
