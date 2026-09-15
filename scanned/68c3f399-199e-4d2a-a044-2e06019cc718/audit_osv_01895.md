# [H] ALPINE-CVE-2020-25681

## Summary
Severity: High
Advisory: ALPINE-CVE-2020-25681
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-01-20
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-25681
Type: osv

## Affected
- Alpine:v3.10: `dnsmasq` — affected >=0 <2.83-r0
- Alpine:v3.11: `dnsmasq` — affected >=0 <2.83-r0
- Alpine:v3.12: `dnsmasq` — affected >=0 <2.83-r0
- Alpine:v3.13: `dnsmasq` — affected >=0 <2.83-r0
- Alpine:v3.14: `dnsmasq` — affected >=0 <2.83-r0
- Alpine:v3.15: `dnsmasq` — affected >=0 <2.83-r0
- Alpine:v3.16: `dnsmasq` — affected >=0 <2.83-r0
- Alpine:v3.17: `dnsmasq` — affected >=0 <2.83-r0
- Alpine:v3.18: `dnsmasq` — affected >=0 <2.83-r0
- Alpine:v3.19: `dnsmasq` — affected >=0 <2.83-r0
- Alpine:v3.20: `dnsmasq` — affected >=0 <2.83-r0
- Alpine:v3.21: `dnsmasq` — affected >=0 <2.83-r0
- Alpine:v3.22: `dnsmasq` — affected >=0 <2.83-r0
- Alpine:v3.23: `dnsmasq` — affected >=0 <2.83-r0
- Alpine:v3.24: `dnsmasq` — affected >=0 <2.83-r0

## Details
A flaw was found in dnsmasq before version 2.83. A heap-based buffer overflow was discovered in the way RRSets are sorted before validating with DNSSEC data. An attacker on the network, who can forge DNS replies such as that they are accepted as valid, could use this flaw to cause a buffer overflow with arbitrary data in a heap memory segment, possibly executing code on the machine. The highest threat from this vulnerability is to data confidentiality and integrity as well as system availability.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-25681
