# [H] ALPINE-CVE-2018-15501

## Summary
Severity: High
Advisory: ALPINE-CVE-2018-15501
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.9
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-08-18
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-15501
Type: osv

## Affected
- Alpine:v3.10: `libgit2` — affected >=0.27.0 <0.27.4-r0
- Alpine:v3.11: `libgit2` — affected >=0.27.0 <0.27.4-r0
- Alpine:v3.9: `libgit2` — affected >=0.27.0 <0.27.4-r0

## Details
In ng_pkt in transports/smart_pkt.c in libgit2 before 0.26.6 and 0.27.x before 0.27.4, a remote attacker can send a crafted smart-protocol "ng" packet that lacks a '\0' byte to trigger an out-of-bounds read that leads to DoS.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-15501
