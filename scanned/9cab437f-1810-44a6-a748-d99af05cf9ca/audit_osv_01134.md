# [H] ALPINE-CVE-2018-20679

## Summary
Severity: High
Advisory: ALPINE-CVE-2018-20679
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.9
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-01-09
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-20679
Type: osv

## Affected
- Alpine:v3.10: `busybox` — affected >=0 <1.29.3-r10
- Alpine:v3.11: `busybox` — affected >=0 <1.29.3-r10
- Alpine:v3.12: `busybox` — affected >=0 <1.29.3-r10
- Alpine:v3.13: `busybox` — affected >=0 <1.29.3-r10
- Alpine:v3.14: `busybox` — affected >=0 <1.29.3-r10
- Alpine:v3.15: `busybox` — affected >=0 <1.29.3-r10
- Alpine:v3.16: `busybox` — affected >=0 <1.29.3-r10
- Alpine:v3.17: `busybox` — affected >=0 <1.29.3-r10
- Alpine:v3.18: `busybox` — affected >=0 <1.29.3-r10
- Alpine:v3.19: `busybox` — affected >=0 <1.29.3-r10
- Alpine:v3.20: `busybox` — affected >=0 <1.29.3-r10
- Alpine:v3.21: `busybox` — affected >=0 <1.29.3-r10
- Alpine:v3.22: `busybox` — affected >=0 <1.29.3-r10
- Alpine:v3.23: `busybox` — affected >=0 <1.29.3-r10
- Alpine:v3.24: `busybox` — affected >=0 <1.29.3-r10
- Alpine:v3.9: `busybox` — affected >=0 <1.29.3-r10

## Details
An issue was discovered in BusyBox before 1.30.0. An out of bounds read in udhcp components (consumed by the DHCP server, client, and relay) allows a remote attacker to leak sensitive information from the stack by sending a crafted DHCP message. This is related to verification in udhcp_get_option() in networking/udhcp/common.c that 4-byte options are indeed 4 bytes.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-20679
