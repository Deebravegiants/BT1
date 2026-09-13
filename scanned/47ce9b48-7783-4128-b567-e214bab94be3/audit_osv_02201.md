# [M] ALPINE-CVE-2021-31808

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2021-31808
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-05-27
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-31808
Type: osv

## Affected
- Alpine:v3.10: `squid` — affected >=5.0 <4.15-r0
- Alpine:v3.11: `squid` — affected >=5.0 <4.15-r0
- Alpine:v3.12: `squid` — affected >=5.0 <4.15-r0
- Alpine:v3.13: `squid` — affected >=5.0 <5.0.6-r0
- Alpine:v3.14: `squid` — affected >=5.0 <5.0.6-r0
- Alpine:v3.15: `squid` — affected >=5.0 <5.0.6-r0
- Alpine:v3.16: `squid` — affected >=5.0 <5.0.6-r0
- Alpine:v3.17: `squid` — affected >=5.0 <5.0.6-r0
- Alpine:v3.18: `squid` — affected >=5.0 <5.0.6-r0
- Alpine:v3.19: `squid` — affected >=5.0 <5.0.6-r0
- Alpine:v3.20: `squid` — affected >=5.0 <5.0.6-r0
- Alpine:v3.21: `squid` — affected >=5.0 <5.0.6-r0
- Alpine:v3.22: `squid` — affected >=5.0 <5.0.6-r0
- Alpine:v3.23: `squid` — affected >=5.0 <5.0.6-r0
- Alpine:v3.24: `squid` — affected >=5.0 <5.0.6-r0

## Details
An issue was discovered in Squid before 4.15 and 5.x before 5.0.6. Due to an input-validation bug, it is vulnerable to a Denial of Service attack (against all clients using the proxy). A client sends an HTTP Range request to trigger this.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-31808
