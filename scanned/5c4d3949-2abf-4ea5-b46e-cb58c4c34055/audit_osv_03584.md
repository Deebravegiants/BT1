# [M] ALPINE-CVE-2026-32883

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-32883
Ecosystem: Alpine:v3.24
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2026-03-30
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-32883
Type: osv

## Affected
- Alpine:v3.24: `botan3` — affected >=0 <3.11.0-r0

## Details
Botan is a C++ cryptography library. From version 3.0.0 to before version 3.11.0, during X509 path validation, OCSP responses were checked for an appropriate status code, but critically omitted verifying the signature of the OCSP response itself. This issue has been patched in version 3.11.0.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-32883
