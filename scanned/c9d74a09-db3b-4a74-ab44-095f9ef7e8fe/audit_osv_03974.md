# [M] ALPINE-CVE-2026-8458

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-8458
Ecosystem: Alpine:v3.23, Alpine:v3.24
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2026-07-03
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-8458
Type: osv

## Affected
- Alpine:v3.23: `curl` — affected >=7.46.0 <8.22.0-r0
- Alpine:v3.24: `curl` — affected >=7.46.0 <8.21.0-r0

## Details
libcurl might in some circumstances reuse the wrong connection when asked to
do Negotiate-authenticated ones, even when they are set to use different
'services'.

libcurl features a pool of recent connections so that subsequent requests can
reuse an existing connection to avoid overhead.

When reusing a connection a range of criteria must be met. Due to a logical
error in the code, a request that was issued by an application could
wrongfully reuse an existing connection to the same server that was
authenticated using different services.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-8458
