# [H] JLSEC-2026-1279

## Summary
Severity: High
Advisory: JLSEC-2026-1279
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/JLSEC-2026-1279
Type: osv

## Affected
- Julia: `Soup3_jll` — affected unspecified

## Details
GNOME libsoup before 3.6.1 has an infinite loop, and memory consumption. during the reading of certain patterns of WebSocket data from clients.

## References
- https://gitlab.gnome.org/GNOME/libsoup/-/issues/391
- https://gitlab.gnome.org/GNOME/libsoup/-/merge_requests/410
- https://gitlab.gnome.org/Teams/Releng/security/-/wikis/home
- https://lists.debian.org/debian-lts-announce/2024/12/msg00014.html
