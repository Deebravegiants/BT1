# [M] CVE-2021-47207

## Summary
Severity: Medium
Advisory: CVE-2021-47207
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-04-10
Source: https://osv.dev/vulnerability/CVE-2021-47207
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

ALSA: gus: fix null pointer dereference on pointer block

The pointer block return from snd_gf1_dma_next_block could be
null, so there is a potential null pointer dereference issue.
Fix this by adding a null check before dereference.

## References
- https://git.kernel.org/stable/c/cb09c760c201f82df83babc92a5ffea0a01807fc
- https://git.kernel.org/stable/c/16721797dcef2c7c030ffe73a07f39a65f9323c3
- https://git.kernel.org/stable/c/1ac6cd87d8ddd36c43620f82c4d65b058f725f0f
- https://git.kernel.org/stable/c/3e28e083dcdf03a18a083f8a47b6bb6b1604b5be
- https://git.kernel.org/stable/c/542fa721594a02d2aee0370a764d306ef48d030c
- https://git.kernel.org/stable/c/a0d21bb3279476c777434c40d969ea88ca64f9aa
- https://git.kernel.org/stable/c/ab4c1ebc40f699f48346f634d7b72b9c5193f315
- https://git.kernel.org/stable/c/c6d2cefdd05c4810c416fb8d384b5c377bd977bc
