# [H] JLSEC-2026-1277

## Summary
Severity: High
Advisory: JLSEC-2026-1277
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/JLSEC-2026-1277
Type: osv

## Affected
- Julia: `Soup3_jll` — affected unspecified

## Details
GNOME libsoup before 3.6.0 allows HTTP request smuggling in some configurations because '\0' characters at the end of header names are ignored, i.e., a "Transfer-Encoding\0: chunked" header is treated the same as a "Transfer-Encoding: chunked" header.

## References
- https://gitlab.gnome.org/GNOME/libsoup/-/issues/377
- https://gitlab.gnome.org/GNOME/libsoup/-/merge_requests/402
- https://gitlab.gnome.org/Teams/Releng/security/-/wikis/home
- https://lists.debian.org/debian-lts-announce/2024/12/msg00014.html
