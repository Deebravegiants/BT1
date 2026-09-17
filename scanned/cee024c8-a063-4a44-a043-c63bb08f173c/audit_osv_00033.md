# [H] ALPINE-CVE-2016-10002

## Summary
Severity: High
Advisory: ALPINE-CVE-2016-10002
Ecosystem: Alpine:v3.2, Alpine:v3.3
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2017-01-27
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-10002
Type: osv

## Affected
- Alpine:v3.2: `squid` — affected >=0 <3.5.23-r0
- Alpine:v3.3: `squid` — affected >=0 <3.5.23-r0

## Details
Incorrect processing of responses to If-None-Modified HTTP conditional requests in Squid HTTP Proxy 3.1.10 through 3.1.23, 3.2.0.3 through 3.5.22, and 4.0.1 through 4.0.16 leads to client-specific Cookie data being leaked to other clients. Attack requests can easily be crafted by a client to probe a cache for this information.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-10002
