# [H] ALPINE-CVE-2022-38725

## Summary
Severity: High
Advisory: ALPINE-CVE-2022-38725
Ecosystem: Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-01-23
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-38725
Type: osv

## Affected
- Alpine:v3.17: `syslog-ng` — affected >=0 <3.38.1-r0
- Alpine:v3.18: `syslog-ng` — affected >=0 <3.38.1-r0
- Alpine:v3.19: `syslog-ng` — affected >=0 <3.38.1-r0
- Alpine:v3.20: `syslog-ng` — affected >=0 <3.38.1-r0
- Alpine:v3.21: `syslog-ng` — affected >=0 <3.38.1-r0
- Alpine:v3.22: `syslog-ng` — affected >=0 <3.38.1-r0
- Alpine:v3.23: `syslog-ng` — affected >=0 <3.38.1-r0
- Alpine:v3.24: `syslog-ng` — affected >=0 <3.38.1-r0

## Details
An integer overflow in the RFC3164 parser in One Identity syslog-ng 3.0 through 3.37 allows remote attackers to cause a Denial of Service via crafted syslog input that is mishandled by the tcp or network function. syslog-ng Premium Edition 7.0.30 and syslog-ng Store Box 6.10.0 are also affected.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-38725
