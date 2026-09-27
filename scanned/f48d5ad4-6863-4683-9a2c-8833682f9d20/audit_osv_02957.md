# [H] ALPINE-CVE-2023-6597

## Summary
Severity: High
Advisory: ALPINE-CVE-2023-6597
Ecosystem: Alpine:v3.16, Alpine:v3.17
CVSS: 7.8 (CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:C/C:H/I:H/A:N)
Published: 2024-03-19
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-6597
Type: osv

## Affected
- Alpine:v3.16: `python3` — affected >=0 <3.10.14-r0
- Alpine:v3.17: `python3` — affected >=0 <3.10.14-r0

## Details
An issue was found in the CPython `tempfile.TemporaryDirectory` class affecting versions 3.12.1, 3.11.7, 3.10.13, 3.9.18, and 3.8.18 and prior.

The tempfile.TemporaryDirectory class would dereference symlinks during cleanup of permissions-related errors. This means users which can run privileged programs are potentially able to modify permissions of files referenced by symlinks in some circumstances.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-6597
