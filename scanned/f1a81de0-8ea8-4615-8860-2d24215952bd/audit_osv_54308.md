# [C] CVE-2023-47359

## Summary
Severity: Critical
Advisory: CVE-2023-47359
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-11-07
Source: https://osv.dev/vulnerability/CVE-2023-47359
Type: osv

## Details
Videolan VLC prior to version 3.0.20 contains an incorrect offset read that leads to a Heap-Based Buffer Overflow in function GetPacket() and results in a memory corruption.

## References
- https://lists.debian.org/debian-lts-announce/2023/11/msg00034.html
- https://0xariana.github.io/blog/real_bugs/vlc/mms
