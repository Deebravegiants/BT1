# [C] ALPINE-CVE-2021-3177

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2021-3177
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-01-19
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-3177
Type: osv

## Affected
- Alpine:v3.10: `python3` — affected >=0 <3.7.7-r2
- Alpine:v3.11: `python3` — affected >=0 <3.8.2-r2
- Alpine:v3.12: `python3` — affected >=0 <3.8.5-r1
- Alpine:v3.13: `python3` — affected >=0 <3.8.7-r1
- Alpine:v3.14: `python3` — affected >=0 <3.8.7-r2
- Alpine:v3.15: `python3` — affected >=0 <3.8.7-r2
- Alpine:v3.16: `python3` — affected >=0 <3.8.7-r2
- Alpine:v3.17: `python3` — affected >=0 <3.8.7-r2
- Alpine:v3.18: `python3` — affected >=0 <3.8.7-r2
- Alpine:v3.19: `python3` — affected >=0 <3.8.7-r2
- Alpine:v3.20: `python3` — affected >=0 <3.8.7-r2
- Alpine:v3.21: `python3` — affected >=0 <3.8.7-r2
- Alpine:v3.22: `python3` — affected >=0 <3.8.7-r2
- Alpine:v3.23: `python3` — affected >=0 <3.8.7-r2
- Alpine:v3.24: `python3` — affected >=0 <3.8.7-r2

## Details
Python 3.x through 3.9.1 has a buffer overflow in PyCArg_repr in _ctypes/callproc.c, which may lead to remote code execution in certain Python applications that accept floating-point numbers as untrusted input, as demonstrated by a 1e300 argument to c_double.from_param. This occurs because sprintf is used unsafely.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-3177
