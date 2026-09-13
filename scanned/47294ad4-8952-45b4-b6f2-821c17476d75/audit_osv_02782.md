# [M] ALPINE-CVE-2023-23931

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2023-23931
Ecosystem: Alpine:v3.23, Alpine:v3.24
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:L)
Published: 2023-02-07
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-23931
Type: osv

## Affected
- Alpine:v3.23: `py3-cryptography` — affected >=1.8 <39.0.1-r0
- Alpine:v3.24: `py3-cryptography` — affected >=1.8 <39.0.1-r0

## Details
cryptography is a package designed to expose cryptographic primitives and recipes to Python developers. In affected versions `Cipher.update_into` would accept Python objects which implement the buffer protocol, but provide only immutable buffers. This would allow immutable objects (such as `bytes`) to be mutated, thus violating fundamental rules of Python and resulting in corrupted output. This now correctly raises an exception. This issue has been present since `update_into` was originally introduced in cryptography 1.8.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-23931
