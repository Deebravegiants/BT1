# [H] ALPINE-CVE-2017-8779

## Summary
Severity: High
Advisory: ALPINE-CVE-2017-8779
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-05-04
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-8779
Type: osv

## Affected
- Alpine:v3.10: `rpcbind` — affected >=0 <0.2.4-r0
- Alpine:v3.11: `rpcbind` — affected >=0 <0.2.4-r0
- Alpine:v3.12: `rpcbind` — affected >=0 <0.2.4-r0
- Alpine:v3.13: `rpcbind` — affected >=0 <0.2.4-r0
- Alpine:v3.14: `rpcbind` — affected >=0 <0.2.4-r0
- Alpine:v3.15: `rpcbind` — affected >=0 <0.2.4-r0
- Alpine:v3.16: `rpcbind` — affected >=0 <0.2.4-r0
- Alpine:v3.17: `rpcbind` — affected >=0 <0.2.4-r0
- Alpine:v3.18: `rpcbind` — affected >=0 <0.2.4-r0
- Alpine:v3.19: `rpcbind` — affected >=0 <0.2.4-r0
- Alpine:v3.20: `rpcbind` — affected >=0 <0.2.4-r0
- Alpine:v3.21: `rpcbind` — affected >=0 <0.2.4-r0
- Alpine:v3.22: `rpcbind` — affected >=0 <0.2.4-r0
- Alpine:v3.23: `rpcbind` — affected >=0 <0.2.4-r0
- Alpine:v3.24: `rpcbind` — affected >=0 <0.2.4-r0
- Alpine:v3.7: `rpcbind` — affected >=0 <0.2.4-r0
- Alpine:v3.8: `rpcbind` — affected >=0 <0.2.4-r0
- Alpine:v3.9: `rpcbind` — affected >=0 <0.2.4-r0

## Details
rpcbind through 0.2.4, LIBTIRPC through 1.0.1 and 1.0.2-rc through 1.0.2-rc3, and NTIRPC through 1.4.3 do not consider the maximum RPC data size during memory allocation for XDR strings, which allows remote attackers to cause a denial of service (memory consumption with no subsequent free) via a crafted UDP packet to port 111, aka rpcbomb.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-8779
