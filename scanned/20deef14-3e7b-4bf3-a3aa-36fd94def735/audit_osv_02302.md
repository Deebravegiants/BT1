# [H] ALPINE-CVE-2021-41611

## Summary
Severity: High
Advisory: ALPINE-CVE-2021-41611
Ecosystem: Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-10-18
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-41611
Type: osv

## Affected
- Alpine:v3.13: `squid` — affected >=5.0.6 <5.0.6-r2
- Alpine:v3.14: `squid` — affected >=5.0.6 <5.0.6-r2
- Alpine:v3.15: `squid` — affected >=5.0.6 <5.2-r0
- Alpine:v3.16: `squid` — affected >=5.0.6 <5.2-r0
- Alpine:v3.17: `squid` — affected >=5.0.6 <5.2-r0
- Alpine:v3.18: `squid` — affected >=5.0.6 <5.2-r0
- Alpine:v3.19: `squid` — affected >=5.0.6 <5.2-r0
- Alpine:v3.20: `squid` — affected >=5.0.6 <5.2-r0
- Alpine:v3.21: `squid` — affected >=5.0.6 <5.2-r0
- Alpine:v3.22: `squid` — affected >=5.0.6 <5.2-r0
- Alpine:v3.23: `squid` — affected >=5.0.6 <5.2-r0
- Alpine:v3.24: `squid` — affected >=5.0.6 <5.2-r0

## Details
An issue was discovered in Squid 5.0.6 through 5.1.x before 5.2. When validating an origin server or peer certificate, Squid may incorrectly classify certain certificates as trusted. This problem allows a remote server to obtain security trust well improperly. This indication of trust may be passed along to clients, allowing access to unsafe or hijacked services.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-41611
