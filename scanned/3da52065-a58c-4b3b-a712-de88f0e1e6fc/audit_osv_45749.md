# [H] JLSEC-2026-284

## Summary
Severity: High
Advisory: JLSEC-2026-284
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-04-28
Source: https://osv.dev/vulnerability/JLSEC-2026-284
Type: osv

## Affected
- Julia: `Xorg_libXpm_jll` — affected >=0 <3.5.17+0

## Details
A flaw was found in libXpm. This issue occurs when parsing a file with a comment not closed; the end-of-file condition will not be detected, leading to an infinite loop and resulting in a Denial of Service in the application linked to the library.

## References
- http://www.openwall.com/lists/oss-security/2023/10/03/1
- http://www.openwall.com/lists/oss-security/2023/10/03/10
- https://bugzilla.redhat.com/show_bug.cgi?id=2160092
- https://gitlab.freedesktop.org/xorg/lib/libxpm/-/commit/a3a7c6dcc3b629d7650148
- https://gitlab.freedesktop.org/xorg/lib/libxpm/-/merge_requests/9
- https://lists.debian.org/debian-lts-announce/2023/06/msg00021.html
- https://lists.x.org/archives/xorg-announce/2023-January/003312.html
