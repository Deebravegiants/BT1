# [H] ALPINE-CVE-2026-33630

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-33630
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-09-03
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-33630
Type: osv

## Affected
- Alpine:v3.21: `c-ares` — affected >=0 <1.34.8-r0
- Alpine:v3.22: `c-ares` — affected >=0 <1.34.8-r0
- Alpine:v3.23: `c-ares` — affected >=0 <1.34.8-r0
- Alpine:v3.24: `c-ares` — affected >=0 <1.34.8-r0

## Details
c-ares is an asynchronous resolver library. From ver 1.32.3 until 1.34.7, a use-after-free / double-free in c-ares' query-completion handling. The same flaw — a query's callback being invoked while the query is still linked in the channel's internal lookup structures — is present at multiple points in the resend/finish path (timeout handling, response handling, and query dispatch). If the query, or for ares_getaddrinfo() the owning host_query, is freed as a side effect of that callback, it is then accessed and/or freed a second time. This vulnerability is fixed in ver 1.34.7.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-33630
