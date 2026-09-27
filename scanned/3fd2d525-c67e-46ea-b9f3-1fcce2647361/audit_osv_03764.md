# [M] ALPINE-CVE-2026-48101

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-48101
Ecosystem: Alpine:v3.24
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2026-06-05
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-48101
Type: osv

## Affected
- Alpine:v3.24: `7zip` — affected >=0 <26.01-r0

## Details
7-Zip is a file archiver with a high compression ratio. Versions 9.21 through 26.00 contain an An uninitialized memory disclosure vulnerability in the UEFI capsule (.scap) parser in 7-Zip. The OpenCapsule function allocates a heap buffer of attacker-declared CapsuleImageSize (up to 1 GiB) without zero-initialization, then reads the file contents into it with ReadStream_FALSE whose return value is silently discarded. If the file is truncated, the unread tail of the buffer retains uninitialized heap memory, which is then exposed as extracted file content via GetStream. Version 26.0.1 fixes the issue.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-48101
