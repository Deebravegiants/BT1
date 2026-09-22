# [H] ALPINE-CVE-2025-5244

## Summary
Severity: High
Advisory: ALPINE-CVE-2025-5244
Ecosystem: Alpine:v3.22
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-05-27
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-5244
Type: osv

## Affected
- Alpine:v3.22: `binutils` — affected >=0 <2.44-r3

## Details
A vulnerability was found in GNU Binutils up to 2.44. It has been rated as critical. Affected by this issue is the function elf_gc_sweep of the file bfd/elflink.c of the component ld. The manipulation leads to memory corruption. An attack has to be approached locally. The exploit has been disclosed to the public and may be used. Upgrading to version 2.45 is able to address this issue. It is recommended to upgrade the affected component.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-5244
