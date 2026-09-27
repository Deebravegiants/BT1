# [M] ALPINE-CVE-2021-22876

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2021-22876
Ecosystem: Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2021-04-01
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-22876
Type: osv

## Affected
- Alpine:v3.12: `curl` — affected >=0 <7.76.0-r0
- Alpine:v3.13: `curl` — affected >=0 <7.76.0-r0
- Alpine:v3.14: `curl` — affected >=0 <7.76.0-r0
- Alpine:v3.15: `curl` — affected >=0 <7.76.0-r0
- Alpine:v3.16: `curl` — affected >=0 <7.76.0-r0
- Alpine:v3.17: `curl` — affected >=0 <7.76.0-r0
- Alpine:v3.18: `curl` — affected >=0 <7.76.0-r0
- Alpine:v3.19: `curl` — affected >=0 <7.76.0-r0
- Alpine:v3.20: `curl` — affected >=0 <7.76.0-r0
- Alpine:v3.21: `curl` — affected >=0 <7.76.0-r0
- Alpine:v3.22: `curl` — affected >=0 <7.76.0-r0
- Alpine:v3.23: `curl` — affected >=0 <7.76.0-r0
- Alpine:v3.24: `curl` — affected >=0 <7.76.0-r0

## Details
curl 7.1.1 to and including 7.75.0 is vulnerable to an "Exposure of Private Personal Information to an Unauthorized Actor" by leaking credentials in the HTTP Referer: header. libcurl does not strip off user credentials from the URL when automatically populating the Referer: HTTP request header field in outgoing HTTP requests, and therefore risks leaking sensitive data to the server that is the target of the second HTTP request.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-22876
