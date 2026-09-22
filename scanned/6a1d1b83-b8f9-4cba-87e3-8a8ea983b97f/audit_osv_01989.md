# [C] ALPINE-CVE-2020-36242

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2020-36242
Ecosystem: Alpine:v3.13, Alpine:v3.23, Alpine:v3.24
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2021-02-07
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-36242
Type: osv

## Affected
- Alpine:v3.13: `py3-cryptography` — affected >=0 <3.3.2-r0
- Alpine:v3.23: `py3-cryptography` — affected >=0 <3.2.2-r0
- Alpine:v3.24: `py3-cryptography` — affected >=0 <3.2.2-r0

## Details
In the cryptography package before 3.3.2 for Python, certain sequences of update calls to symmetrically encrypt multi-GB values could result in an integer overflow and buffer overflow, as demonstrated by the Fernet class.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-36242
