# [H] JLSEC-2026-365

## Summary
Severity: High
Advisory: JLSEC-2026-365
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-04-30
Source: https://osv.dev/vulnerability/JLSEC-2026-365
Type: osv

## Affected
- Julia: `SDL2_jll` — affected >=0 <2.32.10+0

## Details
A potential memory leak issue was discovered in SDL2 in `GLES_CreateTexture()` function in `SDL_render_gles.c`. The vulnerability allows an attacker to cause a denial of service attack. The vulnerability affects SDL2 v2.0.4 and above. SDL-1.x are not affected.

## References
- https://access.redhat.com/security/cve/CVE-2022-4743
- https://bugzilla.redhat.com/show_bug.cgi?id=2156290
- https://github.com/libsdl-org/SDL/commit/00b67f55727bc0944c3266e2b875440da132ce4b
- https://github.com/libsdl-org/SDL/pull/6269
- https://lists.debian.org/debian-lts-announce/2023/02/msg00008.html
- https://lists.debian.org/debian-lts-announce/2025/11/msg00024.html
- https://security.gentoo.org/glsa/202305-18
