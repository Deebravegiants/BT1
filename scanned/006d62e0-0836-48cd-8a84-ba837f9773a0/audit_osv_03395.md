# [M] ALPINE-CVE-2025-8224

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2025-8224
Ecosystem: Alpine:v3.22
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-07-27
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-8224
Type: osv

## Affected
- Alpine:v3.22: `binutils` — affected >=0 <2.44-r0

## Details
A vulnerability has been found in GNU Binutils 2.44 and classified as problematic. This vulnerability affects the function bfd_elf_get_str_section of the file bfd/elf.c of the component BFD Library. The manipulation leads to null pointer dereference. Local access is required to approach this attack. The exploit has been disclosed to the public and may be used. The name of the patch is db856d41004301b3a56438efd957ef5cabb91530. It is recommended to apply a patch to fix this issue.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-8224
