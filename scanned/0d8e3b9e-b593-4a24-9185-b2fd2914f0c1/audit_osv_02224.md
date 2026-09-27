# [M] ALPINE-CVE-2021-33620

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2021-33620
Ecosystem: Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-05-28
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-33620
Type: osv

## Affected
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
Squid before 4.15 and 5.x before 5.0.6 allows remote servers to cause a denial of service (affecting availability to all clients) via an HTTP response. The issue trigger is a header that can be expected to exist in HTTP traffic without any malicious intent by the server.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-33620
