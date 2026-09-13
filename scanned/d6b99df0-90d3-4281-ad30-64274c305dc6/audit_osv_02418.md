# [H] ALPINE-CVE-2022-22576

## Summary
Severity: High
Advisory: ALPINE-CVE-2022-22576
Ecosystem: Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2022-05-26
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-22576
Type: osv

## Affected
- Alpine:v3.12: `curl` — affected >=7.33.0 <7.79.1-r1
- Alpine:v3.13: `curl` — affected >=7.33.0 <7.79.1-r1
- Alpine:v3.14: `curl` — affected >=7.33.0 <7.79.1-r1
- Alpine:v3.15: `curl` — affected >=7.33.0 <7.80.0-r1
- Alpine:v3.16: `curl` — affected >=7.33.0 <7.83.0-r0
- Alpine:v3.17: `curl` — affected >=7.33.0 <7.83.0-r0
- Alpine:v3.18: `curl` — affected >=7.33.0 <7.83.0-r0
- Alpine:v3.19: `curl` — affected >=7.33.0 <7.83.0-r0
- Alpine:v3.20: `curl` — affected >=7.33.0 <7.83.0-r0
- Alpine:v3.21: `curl` — affected >=7.33.0 <7.83.0-r0
- Alpine:v3.22: `curl` — affected >=7.33.0 <7.83.0-r0
- Alpine:v3.23: `curl` — affected >=7.33.0 <7.83.0-r0
- Alpine:v3.24: `curl` — affected >=7.33.0 <7.83.0-r0

## Details
An improper authentication vulnerability exists in curl 7.33.0 to and including 7.82.0 which might allow reuse OAUTH2-authenticated connections without properly making sure that the connection was authenticated with the same credentials as set for this transfer. This affects SASL-enabled protocols: SMPTP(S), IMAP(S), POP3(S) and LDAP(S) (openldap only).

## References
- https://security.alpinelinux.org/vuln/CVE-2022-22576
