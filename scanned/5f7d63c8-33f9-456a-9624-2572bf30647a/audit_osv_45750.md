# [H] JLSEC-2026-285

## Summary
Severity: High
Advisory: JLSEC-2026-285
Ecosystem: Julia
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-28
Source: https://osv.dev/vulnerability/JLSEC-2026-285
Type: osv

## Affected
- Julia: `Xorg_libXpm_jll` — affected >=0 <3.5.17+0

## Details
A flaw was found in libXpm. When processing files with .Z or .gz extensions, the library calls external programs to compress and uncompress files, relying on the PATH environment variable to find these programs, which could allow a malicious user to execute other programs by manipulating the PATH environment variable.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=2160213
- https://gitlab.freedesktop.org/xorg/lib/libxpm/-/commit/515294bb8023a45ff91669
- https://gitlab.freedesktop.org/xorg/lib/libxpm/-/merge_requests/9
- https://lists.debian.org/debian-lts-announce/2023/06/msg00021.html
- https://lists.x.org/archives/xorg-announce/2023-January/003312.html
