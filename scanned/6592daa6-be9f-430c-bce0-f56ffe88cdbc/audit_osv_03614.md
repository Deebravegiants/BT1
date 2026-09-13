# [M] ALPINE-CVE-2026-34073

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-34073
Ecosystem: Alpine:v3.23, Alpine:v3.24
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2026-03-31
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-34073
Type: osv

## Affected
- Alpine:v3.23: `py3-cryptography` — affected >=0 <46.0.7-r0
- Alpine:v3.24: `py3-cryptography` — affected >=0 <46.0.7-r0

## Details
cryptography is a package designed to expose cryptographic primitives and recipes to Python developers. Prior to version 46.0.6, DNS name constraints were only validated against SANs within child certificates, and not the "peer name" presented during each validation. Consequently, cryptography would allow a peer named bar.example.com to validate against a wildcard leaf certificate for *.example.com, even if the leaf's parent certificate (or upwards) contained an excluded subtree constraint for bar.example.com. This issue has been patched in version 46.0.6.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-34073
