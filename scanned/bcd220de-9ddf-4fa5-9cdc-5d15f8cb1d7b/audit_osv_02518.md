# [H] ALPINE-CVE-2022-27782

## Summary
Severity: High
Advisory: ALPINE-CVE-2022-27782
Ecosystem: Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2022-06-02
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-27782
Type: osv

## Affected
- Alpine:v3.13: `curl` — affected >=0 <7.79.1-r2
- Alpine:v3.14: `curl` — affected >=0 <7.79.1-r2
- Alpine:v3.15: `curl` — affected >=0 <7.80.0-r2
- Alpine:v3.16: `curl` — affected >=0 <7.83.1-r0
- Alpine:v3.17: `curl` — affected >=0 <7.83.1-r0
- Alpine:v3.18: `curl` — affected >=0 <7.83.1-r0
- Alpine:v3.19: `curl` — affected >=0 <7.83.1-r0
- Alpine:v3.20: `curl` — affected >=0 <7.83.1-r0
- Alpine:v3.21: `curl` — affected >=0 <7.83.1-r0
- Alpine:v3.22: `curl` — affected >=0 <7.83.1-r0
- Alpine:v3.23: `curl` — affected >=0 <7.83.1-r0
- Alpine:v3.24: `curl` — affected >=0 <7.83.1-r0

## Details
libcurl would reuse a previously created connection even when a TLS or SSHrelated option had been changed that should have prohibited reuse.libcurl keeps previously used connections in a connection pool for subsequenttransfers to reuse if one of them matches the setup. However, several TLS andSSH settings were left out from the configuration match checks, making themmatch too easily.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-27782
