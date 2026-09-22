# [H] ALPINE-CVE-2020-11100

## Summary
Severity: High
Advisory: ALPINE-CVE-2020-11100
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.9
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-04-02
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-11100
Type: osv

## Affected
- Alpine:v3.10: `haproxy` — affected >=1.8.0 <2.0.14-r0
- Alpine:v3.11: `haproxy` — affected >=1.8.0 <2.0.14-r0
- Alpine:v3.12: `haproxy` — affected >=1.8.0 <2.1.4-r0
- Alpine:v3.13: `haproxy` — affected >=1.8.0 <2.1.4-r0
- Alpine:v3.14: `haproxy` — affected >=1.8.0 <2.1.4-r0
- Alpine:v3.15: `haproxy` — affected >=1.8.0 <2.1.4-r0
- Alpine:v3.16: `haproxy` — affected >=1.8.0 <2.1.4-r0
- Alpine:v3.17: `haproxy` — affected >=1.8.0 <2.1.4-r0
- Alpine:v3.18: `haproxy` — affected >=1.8.0 <2.1.4-r0
- Alpine:v3.19: `haproxy` — affected >=1.8.0 <2.1.4-r0
- Alpine:v3.20: `haproxy` — affected >=1.8.0 <2.1.4-r0
- Alpine:v3.21: `haproxy` — affected >=1.8.0 <2.1.4-r0
- Alpine:v3.22: `haproxy` — affected >=1.8.0 <2.1.4-r0
- Alpine:v3.23: `haproxy` — affected >=1.8.0 <2.1.4-r0
- Alpine:v3.24: `haproxy` — affected >=1.8.0 <2.1.4-r0
- Alpine:v3.9: `haproxy` — affected >=1.8.0 <1.8.25-r0

## Details
In hpack_dht_insert in hpack-tbl.c in the HPACK decoder in HAProxy 1.8 through 2.x before 2.1.4, a remote attacker can write arbitrary bytes around a certain location on the heap via a crafted HTTP/2 request, possibly causing remote code execution.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-11100
