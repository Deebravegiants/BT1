# [M] ALPINE-CVE-2022-32208

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2022-32208
Ecosystem: Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2022-07-07
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-32208
Type: osv

## Affected
- Alpine:v3.13: `curl` — affected >=7.16.4 <7.79.1-r2
- Alpine:v3.14: `curl` — affected >=7.16.4 <7.79.1-r2
- Alpine:v3.15: `curl` — affected >=7.16.4 <7.80.0-r2
- Alpine:v3.16: `curl` — affected >=7.16.4 <7.83.1-r2
- Alpine:v3.17: `curl` — affected >=7.16.4 <7.84.0-r0
- Alpine:v3.18: `curl` — affected >=7.16.4 <7.84.0-r0
- Alpine:v3.19: `curl` — affected >=7.16.4 <7.84.0-r0
- Alpine:v3.20: `curl` — affected >=7.16.4 <7.84.0-r0
- Alpine:v3.21: `curl` — affected >=7.16.4 <7.84.0-r0
- Alpine:v3.22: `curl` — affected >=7.16.4 <7.84.0-r0
- Alpine:v3.23: `curl` — affected >=7.16.4 <7.84.0-r0
- Alpine:v3.24: `curl` — affected >=7.16.4 <7.84.0-r0

## Details
When curl < 7.84.0 does FTP transfers secured by krb5, it handles message verification failures wrongly. This flaw makes it possible for a Man-In-The-Middle attack to go unnoticed and even allows it to inject data to the client.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-32208
