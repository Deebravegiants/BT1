# [M] ALPINE-CVE-2024-27982

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2024-27982
Ecosystem: Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:L)
Published: 2024-05-07
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-27982
Type: osv

## Affected
- Alpine:v3.17: `nodejs` — affected >=0 <18.20.1-r0
- Alpine:v3.18: `nodejs` — affected >=0 <18.20.1-r0
- Alpine:v3.19: `nodejs` — affected >=0 <20.12.1-r0
- Alpine:v3.20: `nodejs` — affected >=0 <20.12.1-r0
- Alpine:v3.21: `nodejs` — affected >=0 <20.12.1-r0
- Alpine:v3.22: `nodejs` — affected >=0 <20.12.1-r0
- Alpine:v3.23: `nodejs` — affected >=0 <20.12.1-r0
- Alpine:v3.24: `nodejs` — affected >=0 <20.12.1-r0

## Details
The team has identified a critical vulnerability in the http server of the most recent version of Node, where malformed headers can lead to HTTP request smuggling. Specifically, if a space is placed before a content-length header, it is not interpreted correctly, enabling attackers to smuggle in a second request within the body of the first.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-27982
