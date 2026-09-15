# [H] ALPINE-CVE-2019-12105

## Summary
Severity: High
Advisory: ALPINE-CVE-2019-12105
Ecosystem: Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:H)
Published: 2019-09-10
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-12105
Type: osv

## Affected
- Alpine:v3.12: `supervisor` — affected >=0 <4.1.0-r0
- Alpine:v3.13: `supervisor` — affected >=0 <4.1.0-r0
- Alpine:v3.14: `supervisor` — affected >=0 <4.1.0-r0
- Alpine:v3.15: `supervisor` — affected >=0 <4.1.0-r0
- Alpine:v3.16: `supervisor` — affected >=0 <4.1.0-r0
- Alpine:v3.17: `supervisor` — affected >=0 <4.1.0-r0
- Alpine:v3.18: `supervisor` — affected >=0 <4.1.0-r0
- Alpine:v3.19: `supervisor` — affected >=0 <4.1.0-r0
- Alpine:v3.20: `supervisor` — affected >=0 <4.1.0-r0
- Alpine:v3.21: `supervisor` — affected >=0 <4.1.0-r0
- Alpine:v3.22: `supervisor` — affected >=0 <4.1.0-r0
- Alpine:v3.23: `supervisor` — affected >=0 <4.1.0-r0
- Alpine:v3.24: `supervisor` — affected >=0 <4.1.0-r0

## Details
In Supervisor through 4.0.2, an unauthenticated user can read log files or restart a service. Note: The maintainer responded that the affected component, inet_http_server, is not enabled by default but if the user enables it and does not set a password, Supervisor logs a warning message. The maintainer indicated the ability to run an open server will not be removed but an additional warning was added to the documentation

## References
- https://security.alpinelinux.org/vuln/CVE-2019-12105
