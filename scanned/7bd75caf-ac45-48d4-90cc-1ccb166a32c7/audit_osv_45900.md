# [C] JLSEC-2026-457

## Summary
Severity: Critical
Advisory: JLSEC-2026-457
Ecosystem: Julia
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-07
Source: https://osv.dev/vulnerability/JLSEC-2026-457
Type: osv

## Affected
- Julia: `FreeType2_jll` — affected >=0 <2.13.1+0

## Details
FreeType commit 1e2eb65048f75c64b68708efed6ce904c31f3b2f was discovered to contain a heap buffer overflow via the function `sfnt_init_face`.

## References
- https://gitlab.freedesktop.org/freetype/freetype/-/issues/1138
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/EFPNRKDLCXHZVYYQLQMP44UHLU32GA6Z/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/FDU2FOEMCEF6WVR6ZBIH5MT5O7FAK6UP/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/IWQ7IB2A75MEHM63WEUXBYEC7OR5SGDY/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/NYVC2NPKKXKP3TWJWG4ONYWNO6ZPHLA5/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/TCEMWCM46PKM4U5ENRASPKQD6JDOLKRU/
- https://security.gentoo.org/glsa/202402-06
