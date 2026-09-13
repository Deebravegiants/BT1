# [M] CVE-2021-47193

## Summary
Severity: Medium
Advisory: CVE-2021-47193
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-04-10
Source: https://osv.dev/vulnerability/CVE-2021-47193
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

scsi: pm80xx: Fix memory leak during rmmod

Driver failed to release all memory allocated. This would lead to memory
leak during driver removal.

Properly free memory when the module is removed.

## References
- https://lists.debian.org/debian-lts-announce/2025/10/msg00007.html
- https://git.kernel.org/stable/c/0c4398f2ee030d5753f6b0ad83f0ed9077851d9a
- https://git.kernel.org/stable/c/51e6ed83bb4ade7c360551fa4ae55c4eacea354b
- https://git.kernel.org/stable/c/269a4311b15f68d24e816f43f123888f241ed13d
