# [H] ALPINE-CVE-2019-15163

## Summary
Severity: High
Advisory: ALPINE-CVE-2019-15163
Ecosystem: Alpine:v3.10, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-10-03
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-15163
Type: osv

## Affected
- Alpine:v3.10: `libpcap` — affected >=0 <1.1.1-r0
- Alpine:v3.12: `libpcap` — affected >=0 <1.9.1-r0
- Alpine:v3.13: `libpcap` — affected >=0 <1.9.1-r0
- Alpine:v3.14: `libpcap` — affected >=0 <1.9.1-r0
- Alpine:v3.15: `libpcap` — affected >=0 <1.9.1-r0
- Alpine:v3.16: `libpcap` — affected >=0 <1.9.1-r0
- Alpine:v3.17: `libpcap` — affected >=0 <1.9.1-r0
- Alpine:v3.18: `libpcap` — affected >=0 <1.9.1-r0
- Alpine:v3.19: `libpcap` — affected >=0 <1.9.1-r0
- Alpine:v3.20: `libpcap` — affected >=0 <1.9.1-r0
- Alpine:v3.21: `libpcap` — affected >=0 <1.9.1-r0
- Alpine:v3.22: `libpcap` — affected >=0 <1.9.1-r0
- Alpine:v3.23: `libpcap` — affected >=0 <1.9.1-r0
- Alpine:v3.24: `libpcap` — affected >=0 <1.9.1-r0

## Details
rpcapd/daemon.c in libpcap before 1.9.1 allows attackers to cause a denial of service (NULL pointer dereference and daemon crash) if a crypt() call fails.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-15163
