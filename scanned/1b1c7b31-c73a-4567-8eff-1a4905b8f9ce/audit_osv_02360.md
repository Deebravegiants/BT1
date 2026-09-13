# [H] ALPINE-CVE-2021-46828

## Summary
Severity: High
Advisory: ALPINE-CVE-2021-46828
Ecosystem: Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-07-20
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-46828
Type: osv

## Affected
- Alpine:v3.13: `libtirpc` — affected >=0 <1.3.1-r1
- Alpine:v3.14: `libtirpc` — affected >=0 <1.3.2-r1
- Alpine:v3.15: `libtirpc` — affected >=0 <1.3.2-r1
- Alpine:v3.16: `libtirpc` — affected >=0 <1.3.2-r1
- Alpine:v3.17: `libtirpc` — affected >=0 <1.3.2-r2
- Alpine:v3.18: `libtirpc` — affected >=0 <1.3.2-r2
- Alpine:v3.19: `libtirpc` — affected >=0 <1.3.2-r2
- Alpine:v3.20: `libtirpc` — affected >=0 <1.3.2-r2
- Alpine:v3.21: `libtirpc` — affected >=0 <1.3.2-r2
- Alpine:v3.22: `libtirpc` — affected >=0 <1.3.2-r2
- Alpine:v3.23: `libtirpc` — affected >=0 <1.3.2-r2
- Alpine:v3.24: `libtirpc` — affected >=0 <1.3.2-r2

## Details
In libtirpc before 1.3.3rc1, remote attackers could exhaust the file descriptors of a process that uses libtirpc because idle TCP connections are mishandled. This can, in turn, lead to an svc_run infinite loop without accepting new connections.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-46828
