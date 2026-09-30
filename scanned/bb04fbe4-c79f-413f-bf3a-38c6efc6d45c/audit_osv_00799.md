# [M] ALPINE-CVE-2017-9038

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2017-9038
Ecosystem: Alpine:v3.6
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-05-18
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-9038
Type: osv

## Affected
- Alpine:v3.6: `binutils` — affected >=0 <2.28-r3

## Details
GNU Binutils 2.28 allows remote attackers to cause a denial of service (heap-based buffer over-read and application crash) via a crafted ELF file, related to the byte_get_little_endian function in elfcomm.c, the get_unwind_section_word function in readelf.c, and ARM unwind information that contains invalid word offsets.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-9038
