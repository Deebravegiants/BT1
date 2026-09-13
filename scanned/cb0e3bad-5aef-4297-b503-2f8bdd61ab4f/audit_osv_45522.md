# [H] JLSEC-2026-127

## Summary
Severity: High
Advisory: JLSEC-2026-127
Ecosystem: Julia
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-04-17
Source: https://osv.dev/vulnerability/JLSEC-2026-127
Type: osv

## Affected
- Julia: `SDL2_ttf_jll` — affected >=0 <2.24.0+0

## Details
`SDL_ttf` v2.0.18 and below was discovered to contain an arbitrary memory write via the function `TTF_RenderText_Solid()`. This vulnerability is triggered via a crafted TTF file.

## References
- https://github.com/libsdl-org/SDL_ttf/commit/db1b41ab8bde6723c24b866e466cad78c2fa0448
- https://github.com/libsdl-org/SDL_ttf/issues/187
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/EAGMQMRQDTZFQW64JEW3O6HY3JYLAAHT/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/RXI3MDPR24W5557G34YHWOP2MOK6BTGB/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/XPYTEBBNHCDGPVFACC5RC5K2FZUCYTPZ/
