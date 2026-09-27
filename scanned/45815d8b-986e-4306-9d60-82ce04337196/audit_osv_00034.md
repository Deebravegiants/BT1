# [H] ALPINE-CVE-2016-10003

## Summary
Severity: High
Advisory: ALPINE-CVE-2016-10003
Ecosystem: Alpine:v3.2, Alpine:v3.3
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2017-01-27
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-10003
Type: osv

## Affected
- Alpine:v3.2: `squid` — affected >=3.5.0.1 <3.5.23-r0
- Alpine:v3.3: `squid` — affected >=3.5.0.1 <3.5.23-r0

## Details
Incorrect HTTP Request header comparison in Squid HTTP Proxy 3.5.0.1 through 3.5.22, and 4.0.1 through 4.0.16 results in Collapsed Forwarding feature mistakenly identifying some private responses as being suitable for delivery to multiple clients.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-10003
