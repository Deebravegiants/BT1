# [M] ALPINE-CVE-2021-3468

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2021-3468
Ecosystem: Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-06-02
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-3468
Type: osv

## Affected
- Alpine:v3.11: `avahi` — affected >=0.6 <0.8-r1
- Alpine:v3.12: `avahi` — affected >=0.6 <0.8-r1
- Alpine:v3.13: `avahi` — affected >=0.6 <0.8-r3
- Alpine:v3.14: `avahi` — affected >=0.6 <0.8-r4
- Alpine:v3.15: `avahi` — affected >=0.6 <0.8-r4
- Alpine:v3.16: `avahi` — affected >=0.6 <0.8-r4
- Alpine:v3.17: `avahi` — affected >=0.6 <0.8-r4
- Alpine:v3.18: `avahi` — affected >=0.6 <0.8-r4
- Alpine:v3.19: `avahi` — affected >=0.6 <0.8-r4
- Alpine:v3.20: `avahi` — affected >=0.6 <0.8-r4
- Alpine:v3.21: `avahi` — affected >=0.6 <0.8-r4
- Alpine:v3.22: `avahi` — affected >=0.6 <0.8-r4
- Alpine:v3.23: `avahi` — affected >=0.6 <0.8-r4
- Alpine:v3.24: `avahi` — affected >=0.6 <0.8-r4

## Details
A flaw was found in avahi in versions 0.6 up to 0.8. The event used to signal the termination of the client connection on the avahi Unix socket is not correctly handled in the client_work function, allowing a local attacker to trigger an infinite loop. The highest threat from this vulnerability is to the availability of the avahi service, which becomes unresponsive after this flaw is triggered.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-3468
