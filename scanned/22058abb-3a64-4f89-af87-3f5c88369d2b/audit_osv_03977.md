# [C] ALPINE-CVE-2026-8924

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2026-8924
Ecosystem: Alpine:v3.23, Alpine:v3.24
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-07-03
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-8924
Type: osv

## Affected
- Alpine:v3.23: `curl` — affected >=7.46.0 <8.22.0-r0
- Alpine:v3.24: `curl` — affected >=7.46.0 <8.21.0-r0

## Details
A flaw in curl’s cookie parsing logic allows a malicious HTTP server to set
'super cookies' that bypass the Public Suffix List check. This enables an
attacker-controlled origin to inject cookies that curl subsequently scopes and
transmits to unrelated third-party domains.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-8924
