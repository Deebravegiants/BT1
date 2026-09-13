# [H] JLSEC-2026-283

## Summary
Severity: High
Advisory: JLSEC-2026-283
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-04-28
Source: https://osv.dev/vulnerability/JLSEC-2026-283
Type: osv

## Affected
- Julia: `Xorg_libXpm_jll` — affected >=0 <3.5.17+0

## Details
A flaw was found in libXpm. When processing a file with width of 0 and a very large height, some parser functions will be called repeatedly and can lead to an infinite loop, resulting in a Denial of Service in the application linked to the library.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=2160193
- https://gitlab.freedesktop.org/xorg/lib/libxpm/-/commit/f80fa6ae47ad4a5beacb28
- https://gitlab.freedesktop.org/xorg/lib/libxpm/-/merge_requests/9
- https://lists.debian.org/debian-lts-announce/2023/06/msg00021.html
- https://lists.x.org/archives/xorg-announce/2023-January/003312.html
