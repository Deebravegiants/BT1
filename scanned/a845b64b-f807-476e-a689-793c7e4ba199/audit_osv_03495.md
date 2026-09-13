# [M] ALPINE-CVE-2026-21712

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-21712
Ecosystem: Alpine:v3.23, Alpine:v3.24
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-03-30
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-21712
Type: osv

## Affected
- Alpine:v3.23: `nodejs` — affected >=0 <24.14.1-r0
- Alpine:v3.24: `nodejs` — affected >=0 <24.14.1-r0

## Details
A flaw in Node.js URL processing causes an assertion failure in native code when `url.format()` is called with a malformed internationalized domain name (IDN) containing invalid characters, crashing the Node.js process.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-21712
