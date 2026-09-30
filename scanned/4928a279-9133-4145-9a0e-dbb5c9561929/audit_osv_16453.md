# [M] CVE-2019-7147

## Summary
Severity: Medium
Advisory: CVE-2019-7147
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-01-29
Source: https://osv.dev/vulnerability/CVE-2019-7147
Type: osv

## Details
A buffer over-read exists in the function crc64ib in crc64.c in nasmlib in Netwide Assembler (NASM) 2.14rc16. A crafted asm input can cause segmentation faults, leading to denial-of-service.

## References
- https://bugzilla.nasm.us/show_bug.cgi?id=3392544
