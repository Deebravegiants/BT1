# [M] ALPINE-CVE-2018-6759

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2018-6759
Ecosystem: Alpine:v3.7, Alpine:v3.8
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-02-06
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-6759
Type: osv

## Affected
- Alpine:v3.7: `binutils` — affected >=0 <2.30-r2
- Alpine:v3.8: `binutils` — affected >=0 <2.30-r6

## Details
The bfd_get_debug_link_info_1 function in opncls.c in the Binary File Descriptor (BFD) library (aka libbfd), as distributed in GNU Binutils 2.30, has an unchecked strnlen operation. Remote attackers could leverage this vulnerability to cause a denial of service (segmentation fault) via a crafted ELF file.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-6759
