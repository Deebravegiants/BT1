# [M] ALPINE-CVE-2021-22925

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2021-22925
Ecosystem: Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2021-08-05
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-22925
Type: osv

## Affected
- Alpine:v3.11: `curl` — affected >=7.7 <7.67.0-r5
- Alpine:v3.12: `curl` — affected >=7.7 <7.78.0-r0
- Alpine:v3.13: `curl` — affected >=7.7 <7.78.0-r0
- Alpine:v3.14: `curl` — affected >=7.7 <7.78.0-r0
- Alpine:v3.15: `curl` — affected >=7.7 <7.78.0-r0
- Alpine:v3.16: `curl` — affected >=7.7 <7.78.0-r0
- Alpine:v3.17: `curl` — affected >=7.7 <7.78.0-r0
- Alpine:v3.18: `curl` — affected >=7.7 <7.78.0-r0
- Alpine:v3.19: `curl` — affected >=7.7 <7.78.0-r0
- Alpine:v3.20: `curl` — affected >=7.7 <7.78.0-r0
- Alpine:v3.21: `curl` — affected >=7.7 <7.78.0-r0
- Alpine:v3.22: `curl` — affected >=7.7 <7.78.0-r0
- Alpine:v3.23: `curl` — affected >=7.7 <7.78.0-r0
- Alpine:v3.24: `curl` — affected >=7.7 <7.78.0-r0

## Details
curl supports the `-t` command line option, known as `CURLOPT_TELNETOPTIONS`in libcurl. This rarely used option is used to send variable=content pairs toTELNET servers.Due to flaw in the option parser for sending `NEW_ENV` variables, libcurlcould be made to pass on uninitialized data from a stack based buffer to theserver. Therefore potentially revealing sensitive internal information to theserver using a clear-text network protocol.This could happen because curl did not call and use sscanf() correctly whenparsing the string provided by the application.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-22925
