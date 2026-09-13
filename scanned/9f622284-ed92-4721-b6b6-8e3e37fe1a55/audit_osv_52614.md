# [M] CVE-2021-47644

## Summary
Severity: Medium
Advisory: CVE-2021-47644
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2021-47644
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

media: staging: media: zoran: move videodev alloc

Move some code out of zr36057_init() and create new functions for handling
zr->video_dev. This permit to ease code reading and fix a zr->video_dev
memory leak.

## References
- https://git.kernel.org/stable/c/8dce4b265a5357731058f69645840dabc718c687
- https://git.kernel.org/stable/c/82e3a496eb56da0b9f29fdc5b63cedb3289e91de
- https://git.kernel.org/stable/c/bd01629315ffd5b63da91d0bd529a77d30e55028
- https://git.kernel.org/stable/c/c1ba65100a359fe28cfe37e09e10c99f247cbf1e
- https://git.kernel.org/stable/c/ff3357bffd9fb78f59762d8955afc7382a279079
- https://git.kernel.org/stable/c/1e501ec38796f43e995731d1bcd4173cb1ccfce0
