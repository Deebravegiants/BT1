# [H] CVE-2022-4743

## Summary
Severity: High
Advisory: CVE-2022-4743
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-01-12
Source: https://osv.dev/vulnerability/CVE-2022-4743
Type: osv

## Details
A potential memory leak issue was discovered in SDL2 in GLES_CreateTexture() function in SDL_render_gles.c. The vulnerability allows an attacker to cause a denial of service attack. The vulnerability affects SDL2 v2.0.4 and above. SDL-1.x are not affected.

## References
- https://access.redhat.com/security/cve/CVE-2022-4743
- https://lists.debian.org/debian-lts-announce/2025/11/msg00024.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/4xxx/CVE-2022-4743.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-4743
- https://security.gentoo.org/glsa/202305-18
- https://bugzilla.redhat.com/show_bug.cgi?id=2156290
- https://github.com/libsdl-org/SDL/commit/00b67f55727bc0944c3266e2b875440da132ce4b
- https://github.com/libsdl-org/SDL/pull/6269
- https://lists.debian.org/debian-lts-announce/2023/02/msg00008.html
