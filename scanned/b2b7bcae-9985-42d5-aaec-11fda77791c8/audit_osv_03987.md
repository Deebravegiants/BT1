# [H] ALPINE-CVE-2026-9546

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-9546
Ecosystem: Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-07-03
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-9546
Type: osv

## Affected
- Alpine:v3.23: `curl` — affected >=8.18.0 <8.22.0-r0
- Alpine:v3.24: `curl` — affected >=8.18.0 <8.21.0-r0

## Details
A vulnerability in libcurl caused the HTTP `Referer:` header to persist even
when explicitly cleared. While the documentation states that passing NULL to
`CURLOPT_REFERER` suppresses the header, the option failed to clear the
internal state. As a result the previous referrer string was erroneously
reused and sent in subsequent requests, potentially leaking sensitive
information to unintended servers.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-9546
