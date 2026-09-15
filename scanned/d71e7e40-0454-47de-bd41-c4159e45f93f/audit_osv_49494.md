# [M] CVE-2019-13626

## Summary
Severity: Medium
Advisory: CVE-2019-13626
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-07-17
Source: https://osv.dev/vulnerability/CVE-2019-13626
Type: osv

## Details
SDL (Simple DirectMedia Layer) 2.x through 2.0.9 has a heap-based buffer over-read in Fill_IMA_ADPCM_block, caused by an integer overflow in IMA_ADPCM_decode() in audio/SDL_wave.c.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/GY6FDFPYUJ7YPY3XB5U75VJHBSVRVIKO/
- https://lists.debian.org/debian-lts-announce/2023/02/msg00008.html
- https://security.gentoo.org/glsa/201909-07
- http://lists.opensuse.org/opensuse-security-announce/2019-09/msg00093.html
- http://lists.opensuse.org/opensuse-security-announce/2019-09/msg00094.html
- https://bugzilla.libsdl.org/show_bug.cgi?id=4522
