# [H] ALPINE-CVE-2026-8286

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-8286
Ecosystem: Alpine:v3.23, Alpine:v3.24
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-07-03
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-8286
Type: osv

## Affected
- Alpine:v3.23: `curl` — affected >=7.30.0 <8.22.0-r0
- Alpine:v3.24: `curl` — affected >=7.30.0 <8.21.0-r0

## Details
A vulnerability exists where a new transfer that uses STARTTLS to upgrade the
connection might reuse an existing live connection even though the TLS
configuration mismatches so it should not.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-8286
