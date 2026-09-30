# [H] ALPINE-CVE-2021-22883

## Summary
Severity: High
Advisory: ALPINE-CVE-2021-22883
Ecosystem: Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-03-03
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-22883
Type: osv

## Affected
- Alpine:v3.11: `nodejs` — affected >=0 <12.21.0-r0
- Alpine:v3.12: `nodejs` — affected >=0 <12.21.0-r0
- Alpine:v3.13: `nodejs` — affected >=0 <14.16.0-r0
- Alpine:v3.14: `nodejs` — affected >=0 <14.16.0-r0
- Alpine:v3.15: `nodejs` — affected >=0 <14.16.0-r0
- Alpine:v3.16: `nodejs` — affected >=0 <14.16.0-r0
- Alpine:v3.17: `nodejs` — affected >=0 <14.16.0-r0
- Alpine:v3.18: `nodejs` — affected >=0 <14.16.0-r0
- Alpine:v3.19: `nodejs` — affected >=0 <14.16.0-r0
- Alpine:v3.20: `nodejs` — affected >=0 <14.16.0-r0
- Alpine:v3.21: `nodejs` — affected >=0 <14.16.0-r0
- Alpine:v3.22: `nodejs` — affected >=0 <14.16.0-r0
- Alpine:v3.23: `nodejs` — affected >=0 <14.16.0-r0
- Alpine:v3.24: `nodejs` — affected >=0 <14.16.0-r0

## Details
Node.js before 10.24.0, 12.21.0, 14.16.0, and 15.10.0 is vulnerable to a denial of service attack when too many connection attempts with an 'unknownProtocol' are established. This leads to a leak of file descriptors. If a file descriptor limit is configured on the system, then the server is unable to accept new connections and prevent the process also from opening, e.g. a file. If no file descriptor limit is configured, then this lead to an excessive memory usage and cause the system to run out of memory.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-22883
