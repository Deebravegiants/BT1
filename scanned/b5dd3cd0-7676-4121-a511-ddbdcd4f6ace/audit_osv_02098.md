# [M] ALPINE-CVE-2021-22947

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2021-22947
Ecosystem: Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2021-09-29
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-22947
Type: osv

## Affected
- Alpine:v3.11: `curl` — affected >=7.20.0 <7.79.0-r0
- Alpine:v3.12: `curl` — affected >=7.20.0 <7.79.0-r0
- Alpine:v3.13: `curl` — affected >=7.20.0 <7.79.0-r0
- Alpine:v3.14: `curl` — affected >=7.20.0 <7.79.0-r0
- Alpine:v3.15: `curl` — affected >=7.20.0 <7.79.0-r0
- Alpine:v3.16: `curl` — affected >=7.20.0 <7.79.0-r0
- Alpine:v3.17: `curl` — affected >=7.20.0 <7.79.0-r0
- Alpine:v3.18: `curl` — affected >=7.20.0 <7.79.0-r0
- Alpine:v3.19: `curl` — affected >=7.20.0 <7.79.0-r0
- Alpine:v3.20: `curl` — affected >=7.20.0 <7.79.0-r0
- Alpine:v3.21: `curl` — affected >=7.20.0 <7.79.0-r0
- Alpine:v3.22: `curl` — affected >=7.20.0 <7.79.0-r0
- Alpine:v3.23: `curl` — affected >=7.20.0 <7.79.0-r0
- Alpine:v3.24: `curl` — affected >=7.20.0 <7.79.0-r0

## Details
When curl >= 7.20.0 and <= 7.78.0 connects to an IMAP or POP3 server to retrieve data using STARTTLS to upgrade to TLS security, the server can respond and send back multiple responses at once that curl caches. curl would then upgrade to TLS but not flush the in-queue of cached responses but instead continue using and trustingthe responses it got *before* the TLS handshake as if they were authenticated.Using this flaw, it allows a Man-In-The-Middle attacker to first inject the fake responses, then pass-through the TLS traffic from the legitimate server and trick curl into sending data back to the user thinking the attacker's injected data comes from the TLS-protected server.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-22947
