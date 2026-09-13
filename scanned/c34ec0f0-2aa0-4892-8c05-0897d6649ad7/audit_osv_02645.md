# [M] ALPINE-CVE-2022-41317

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2022-41317
Ecosystem: Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2022-12-25
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-41317
Type: osv

## Affected
- Alpine:v3.19: `squid` — affected >=4.9 <5.7-r0
- Alpine:v3.20: `squid` — affected >=4.9 <5.7-r0
- Alpine:v3.21: `squid` — affected >=4.9 <5.7-r0
- Alpine:v3.22: `squid` — affected >=4.9 <5.7-r0
- Alpine:v3.23: `squid` — affected >=4.9 <5.7-r0
- Alpine:v3.24: `squid` — affected >=4.9 <5.7-r0

## Details
An issue was discovered in Squid 4.9 through 4.17 and 5.0.6 through 5.6. Due to inconsistent handling of internal URIs, there can be Exposure of Sensitive Information about clients using the proxy via an HTTPS request to an internal cache manager URL. This is fixed in 5.7.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-41317
