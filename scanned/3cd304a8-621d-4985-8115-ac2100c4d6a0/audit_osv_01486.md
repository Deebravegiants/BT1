# [M] ALPINE-CVE-2019-17023

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2019-17023
Ecosystem: Alpine:v3.12, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N)
Published: 2020-01-08
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-17023
Type: osv

## Affected
- Alpine:v3.12: `nss` — affected >=0 <3.49-r0
- Alpine:v3.19: `nss` — affected >=0 <3.49-r0
- Alpine:v3.20: `nss` — affected >=0 <3.49-r0
- Alpine:v3.21: `nss` — affected >=0 <3.49-r0
- Alpine:v3.22: `nss` — affected >=0 <3.49-r0
- Alpine:v3.23: `nss` — affected >=0 <3.49-r0
- Alpine:v3.24: `nss` — affected >=0 <3.49-r0

## Details
After a HelloRetryRequest has been sent, the client may negotiate a lower protocol that TLS 1.3, resulting in an invalid state transition in the TLS State Machine. If the client gets into this state, incoming Application Data records will be ignored. This vulnerability affects Firefox < 72.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-17023
