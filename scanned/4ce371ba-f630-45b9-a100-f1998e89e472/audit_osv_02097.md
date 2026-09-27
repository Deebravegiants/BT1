# [H] ALPINE-CVE-2021-22946

## Summary
Severity: High
Advisory: ALPINE-CVE-2021-22946
Ecosystem: Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-09-29
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-22946
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
A user can tell curl >= 7.20.0 and <= 7.78.0 to require a successful upgrade to TLS when speaking to an IMAP, POP3 or FTP server (`--ssl-reqd` on the command line or`CURLOPT_USE_SSL` set to `CURLUSESSL_CONTROL` or `CURLUSESSL_ALL` withlibcurl). This requirement could be bypassed if the server would return a properly crafted but perfectly legitimate response.This flaw would then make curl silently continue its operations **withoutTLS** contrary to the instructions and expectations, exposing possibly sensitive data in clear text over the network.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-22946
