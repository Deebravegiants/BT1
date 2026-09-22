# [H] ALPINE-CVE-2021-31618

## Summary
Severity: High
Advisory: ALPINE-CVE-2021-31618
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-06-15
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-31618
Type: osv

## Affected
- Alpine:v3.10: `apache2` — affected >=0 <2.4.48-r0
- Alpine:v3.11: `apache2` — affected >=0 <2.4.48-r0
- Alpine:v3.12: `apache2` — affected >=0 <2.4.48-r0
- Alpine:v3.13: `apache2` — affected >=0 <2.4.48-r0
- Alpine:v3.14: `apache2` — affected >=0 <2.4.48-r0
- Alpine:v3.15: `apache2` — affected >=0 <2.4.48-r0
- Alpine:v3.16: `apache2` — affected >=0 <2.4.48-r0
- Alpine:v3.17: `apache2` — affected >=0 <2.4.48-r0
- Alpine:v3.18: `apache2` — affected >=0 <2.4.48-r0
- Alpine:v3.19: `apache2` — affected >=0 <2.4.48-r0
- Alpine:v3.20: `apache2` — affected >=0 <2.4.48-r0
- Alpine:v3.21: `apache2` — affected >=0 <2.4.48-r0
- Alpine:v3.22: `apache2` — affected >=0 <2.4.48-r0
- Alpine:v3.23: `apache2` — affected >=0 <2.4.48-r0
- Alpine:v3.24: `apache2` — affected >=0 <2.4.48-r0

## Details
Apache HTTP Server protocol handler for the HTTP/2 protocol checks received request headers against the size limitations as configured for the server and used for the HTTP/1 protocol as well. On violation of these restrictions and HTTP response is sent to the client with a status code indicating why the request was rejected. This rejection response was not fully initialised in the HTTP/2 protocol handler if the offending header was the very first one received or appeared in a a footer. This led to a NULL pointer dereference on initialised memory, crashing reliably the child process. Since such a triggering HTTP/2 request is easy to craft and submit, this can be exploited to DoS the server. This issue affected mod_http2 1.15.17 and Apache HTTP Server version 2.4.47 only. Apache HTTP Server 2.4.47 was never released.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-31618
