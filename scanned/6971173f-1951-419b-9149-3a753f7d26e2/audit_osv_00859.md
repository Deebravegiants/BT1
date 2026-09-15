# [C] ALPINE-CVE-2018-1000005

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2018-1000005
Ecosystem: Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7
CVSS: 9.1 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2018-01-24
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-1000005
Type: osv

## Affected
- Alpine:v3.4: `curl` — affected >=0 <7.58.0-r0
- Alpine:v3.5: `curl` — affected >=0 <7.58.0-r0
- Alpine:v3.6: `curl` — affected >=0 <7.58.0-r0
- Alpine:v3.7: `curl` — affected >=0 <7.58.0-r0

## Details
libcurl 7.49.0 to and including 7.57.0 contains an out bounds read in code handling HTTP/2 trailers. It was reported (https://github.com/curl/curl/pull/2231) that reading an HTTP/2 trailer could mess up future trailers since the stored size was one byte less than required. The problem is that the code that creates HTTP/1-like headers from the HTTP/2 trailer data once appended a string like `:` to the target buffer, while this was recently changed to `: ` (a space was added after the colon) but the following math wasn't updated correspondingly. When accessed, the data is read out of bounds and causes either a crash or that the (too large) data gets passed to client write. This could lead to a denial-of-service situation or an information disclosure if someone has a service that echoes back or uses the trailers for something.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-1000005
