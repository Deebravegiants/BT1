# [H] CVE-2019-12219

## Summary
Severity: High
Advisory: CVE-2019-12219
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-05-20
Source: https://osv.dev/vulnerability/CVE-2019-12219
Type: osv

## Details
An issue was discovered in libSDL2.a in Simple DirectMedia Layer (SDL) 2.0.9 when used in conjunction with libSDL2_image.a in SDL2_image 2.0.4. There is an invalid free error in the SDL function SDL_SetError_REAL at SDL_error.c.

## References
- https://lists.debian.org/debian-lts-announce/2019/07/msg00021.html
- https://lists.debian.org/debian-lts-announce/2019/07/msg00026.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/GY6FDFPYUJ7YPY3XB5U75VJHBSVRVIKO/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/WJ2VRD57UOBT72JUC2DIFHEFCH4N64SW/
- https://usn.ubuntu.com/4238-1/
- https://bugzilla.libsdl.org/show_bug.cgi?id=4625
