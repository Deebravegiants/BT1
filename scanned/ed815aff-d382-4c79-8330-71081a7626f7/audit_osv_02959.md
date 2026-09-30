# [M] ALPINE-CVE-2024-0450

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2024-0450
Ecosystem: Alpine:v3.16, Alpine:v3.17
CVSS: 6.2 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-03-19
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-0450
Type: osv

## Affected
- Alpine:v3.16: `python3` — affected >=0 <3.10.14-r0
- Alpine:v3.17: `python3` — affected >=0 <3.10.14-r0

## Details
An issue was found in the CPython `zipfile` module affecting versions 3.12.1, 3.11.7, 3.10.13, 3.9.18, and 3.8.18 and prior.

The zipfile module is vulnerable to “quoted-overlap” zip-bombs which exploit the zip format to create a zip-bomb with a high compression ratio. The fixed versions of CPython makes the zipfile module reject zip archives which overlap entries in the archive.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-0450
