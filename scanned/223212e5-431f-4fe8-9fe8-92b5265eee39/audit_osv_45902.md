# [H] JLSEC-2026-459

## Summary
Severity: High
Advisory: JLSEC-2026-459
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-05-07
Source: https://osv.dev/vulnerability/JLSEC-2026-459
Type: osv

## Affected
- Julia: `FreeType2_jll` — affected >=0 <2.13.1+0

## Details
FreeType commit 22a0cccb4d9d002f33c1ba7a4b36812c7d4f46b5 was discovered to contain a segmentation violation via the function `FT_Request_Size`.

## References
- http://freetype.com
- https://gitlab.freedesktop.org/freetype/freetype/-/issues/1140
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/EFPNRKDLCXHZVYYQLQMP44UHLU32GA6Z/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/FDU2FOEMCEF6WVR6ZBIH5MT5O7FAK6UP/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/IWQ7IB2A75MEHM63WEUXBYEC7OR5SGDY/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/NYVC2NPKKXKP3TWJWG4ONYWNO6ZPHLA5/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/TCEMWCM46PKM4U5ENRASPKQD6JDOLKRU/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/EFPNRKDLCXHZVYYQLQMP44UHLU32GA6Z/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/FDU2FOEMCEF6WVR6ZBIH5MT5O7FAK6UP/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/IWQ7IB2A75MEHM63WEUXBYEC7OR5SGDY/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/NYVC2NPKKXKP3TWJWG4ONYWNO6ZPHLA5/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/TCEMWCM46PKM4U5ENRASPKQD6JDOLKRU/
- https://security.gentoo.org/glsa/202402-06
