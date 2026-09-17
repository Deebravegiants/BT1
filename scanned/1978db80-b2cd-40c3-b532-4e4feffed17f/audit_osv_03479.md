# [C] ALPINE-CVE-2026-18924

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2026-18924
Ecosystem: Alpine:v3.23, Alpine:v3.24
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H)
Published: 2026-09-06
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-18924
Type: osv

## Affected
- Alpine:v3.23: `curl` — affected >=0 <8.22.0-r0
- Alpine:v3.24: `curl` — affected >=0 <8.22.0-r0

## Details
A flaw in libcurl's handling of HTTP/2 Server Push streams, when the parent
handle is set to share connections with other handles, can lead to
use-after-free in the cleanup process.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-18924
