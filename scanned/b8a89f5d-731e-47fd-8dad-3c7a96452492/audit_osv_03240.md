# [M] ALPINE-CVE-2025-27465

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2025-27465
Ecosystem: Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L)
Published: 2025-07-16
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-27465
Type: osv

## Affected
- Alpine:v3.19: `xen` — affected >=4.9.0 <4.18.5-r1
- Alpine:v3.20: `xen` — affected >=4.9.0 <4.18.5-r1
- Alpine:v3.21: `xen` — affected >=4.9.0 <4.19.2-r2
- Alpine:v3.22: `xen` — affected >=4.9.0 <4.20.1-r0
- Alpine:v3.23: `xen` — affected >=4.9.0 <4.20.1-r0
- Alpine:v3.24: `xen` — affected >=4.9.0 <4.20.1-r0

## Details
Certain instructions need intercepting and emulating by Xen.  In some
cases Xen emulates the instruction by replaying it, using an executable
stub.  Some instructions may raise an exception, which is supposed to be
handled gracefully.  Certain replayed instructions have additional logic
to set up and recover the changes to the arithmetic flags.

For replayed instructions where the flags recovery logic is used, the
metadata for exception handling was incorrect, preventing Xen from
handling the the exception gracefully, treating it as fatal instead.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-27465
