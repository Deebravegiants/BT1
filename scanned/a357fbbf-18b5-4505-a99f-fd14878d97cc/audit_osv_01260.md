# [H] ALPINE-CVE-2018-7643

## Summary
Severity: High
Advisory: ALPINE-CVE-2018-7643
Ecosystem: Alpine:v3.7, Alpine:v3.8
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-03-02
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-7643
Type: osv

## Affected
- Alpine:v3.7: `binutils` — affected >=0 <2.30-r2
- Alpine:v3.8: `binutils` — affected >=0 <2.30-r6

## Details
The display_debug_ranges function in dwarf.c in GNU Binutils 2.30 allows remote attackers to cause a denial of service (integer overflow and application crash) or possibly have unspecified other impact via a crafted ELF file, as demonstrated by objdump.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-7643
