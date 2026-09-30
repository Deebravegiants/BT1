# [M] CVE-2017-14406

## Summary
Severity: Medium
Advisory: CVE-2017-14406
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-09-13
Source: https://osv.dev/vulnerability/CVE-2017-14406
Type: osv

## Details
A NULL pointer dereference was discovered in sync_buffer in interface.c in mpglibDBL, as used in MP3Gain version 1.5.2. The vulnerability causes a segmentation fault and application crash, which leads to remote denial of service.

## References
- https://blogs.gentoo.org/ago/2017/09/08/mp3gain-null-pointer-dereference-in-sync_buffer-mpglibdblinterface-c/
