# [H] ALPINE-CVE-2021-28651

## Summary
Severity: High
Advisory: ALPINE-CVE-2021-28651
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-05-27
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-28651
Type: osv

## Affected
- Alpine:v3.10: `squid` — affected >=2.0 <4.15-r0
- Alpine:v3.11: `squid` — affected >=2.0 <4.15-r0
- Alpine:v3.12: `squid` — affected >=2.0 <4.15-r0
- Alpine:v3.13: `squid` — affected >=2.0 <5.0.6-r0
- Alpine:v3.14: `squid` — affected >=2.0 <5.0.6-r0
- Alpine:v3.15: `squid` — affected >=2.0 <5.0.6-r0
- Alpine:v3.16: `squid` — affected >=2.0 <5.0.6-r0
- Alpine:v3.17: `squid` — affected >=2.0 <5.0.6-r0
- Alpine:v3.18: `squid` — affected >=2.0 <5.0.6-r0
- Alpine:v3.19: `squid` — affected >=2.0 <5.0.6-r0
- Alpine:v3.20: `squid` — affected >=2.0 <5.0.6-r0
- Alpine:v3.21: `squid` — affected >=2.0 <5.0.6-r0
- Alpine:v3.22: `squid` — affected >=2.0 <5.0.6-r0
- Alpine:v3.23: `squid` — affected >=2.0 <5.0.6-r0
- Alpine:v3.24: `squid` — affected >=2.0 <5.0.6-r0

## Details
An issue was discovered in Squid before 4.15 and 5.x before 5.0.6. Due to a buffer-management bug, it allows a denial of service. When resolving a request with the urn: scheme, the parser leaks a small amount of memory. However, there is an unspecified attack methodology that can easily trigger a large amount of memory consumption.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-28651
