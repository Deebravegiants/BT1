# [M] ALPINE-CVE-2025-14104

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2025-14104
Ecosystem: Alpine:v3.22, Alpine:v3.23
CVSS: 6.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:H)
Published: 2025-12-05
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-14104
Type: osv

## Affected
- Alpine:v3.22: `util-linux` — affected >=0 <2.41.6-r0
- Alpine:v3.23: `util-linux` — affected >=0 <2.41.4-r0

## Details
A flaw was found in util-linux. This vulnerability allows a heap buffer overread when processing 256-byte usernames, specifically within the `setpwnam()` function, affecting SUID (Set User ID) login-utils utilities writing to the password database.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-14104
