# [M] CVE-2019-12221

## Summary
Severity: Medium
Advisory: CVE-2019-12221
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-05-20
Source: https://osv.dev/vulnerability/CVE-2019-12221
Type: osv

## Details
An issue was discovered in libSDL2.a in Simple DirectMedia Layer (SDL) 2.0.9 when used in conjunction with libSDL2_image.a in SDL2_image 2.0.4. There is a SEGV in the SDL function SDL_free_REAL at stdlib/SDL_malloc.c.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/GY6FDFPYUJ7YPY3XB5U75VJHBSVRVIKO/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/WJ2VRD57UOBT72JUC2DIFHEFCH4N64SW/
- http://lists.opensuse.org/opensuse-security-announce/2019-09/msg00012.html
- http://lists.opensuse.org/opensuse-security-announce/2019-09/msg00029.html
- https://lists.debian.org/debian-lts-announce/2019/07/msg00021.html
- https://lists.debian.org/debian-lts-announce/2019/07/msg00026.html
- https://usn.ubuntu.com/4238-1/
- https://bugzilla.libsdl.org/show_bug.cgi?id=4628
