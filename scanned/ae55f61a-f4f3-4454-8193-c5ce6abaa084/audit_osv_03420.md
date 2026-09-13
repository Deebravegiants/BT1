# [C] ALPINE-CVE-2026-11564

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2026-11564
Ecosystem: Alpine:v3.23, Alpine:v3.24
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-07-03
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-11564
Type: osv

## Affected
- Alpine:v3.23: `curl` — affected >=8.17.0 <8.22.0-r0
- Alpine:v3.24: `curl` — affected >=8.17.0 <8.21.0-r0

## Details
libcurl keeps previously used connections in a connection pool for subsequent
transfers to reuse if one of them matches the setup.

An easy handle that first uses default native CA trust can continue trusting
the native platform store after the application switches that same handle to
custom CA material for a later transfer.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-11564
