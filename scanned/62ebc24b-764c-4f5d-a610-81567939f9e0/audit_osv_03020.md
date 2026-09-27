# [M] ALPINE-CVE-2024-25629

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2024-25629
Ecosystem: Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-02-23
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-25629
Type: osv

## Affected
- Alpine:v3.16: `c-ares` — affected >=0 <1.19.1-r1
- Alpine:v3.17: `c-ares` — affected >=0 <1.19.1-r1
- Alpine:v3.18: `c-ares` — affected >=0 <1.19.1-r1
- Alpine:v3.19: `c-ares` — affected >=0 <1.27.0-r0
- Alpine:v3.20: `c-ares` — affected >=0 <1.27.0-r0
- Alpine:v3.21: `c-ares` — affected >=0 <1.27.0-r0
- Alpine:v3.22: `c-ares` — affected >=0 <1.27.0-r0
- Alpine:v3.23: `c-ares` — affected >=0 <1.27.0-r0
- Alpine:v3.24: `c-ares` — affected >=0 <1.27.0-r0

## Details
c-ares is a C library for asynchronous DNS requests. `ares__read_line()` is used to parse local configuration files such as `/etc/resolv.conf`, `/etc/nsswitch.conf`, the `HOSTALIASES` file, and if using a c-ares version prior to 1.27.0, the `/etc/hosts` file. If any of these configuration files has an embedded `NULL` character as the first character in a new line, it can lead to attempting to read memory prior to the start of the given buffer which may result in a crash. This issue is fixed in c-ares 1.27.0. No known workarounds exist.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-25629
