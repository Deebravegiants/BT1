# [H] ALPINE-CVE-2018-7208

## Summary
Severity: High
Advisory: ALPINE-CVE-2018-7208
Ecosystem: Alpine:v3.7, Alpine:v3.8
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-02-18
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-7208
Type: osv

## Affected
- Alpine:v3.7: `binutils` — affected >=0 <2.30-r2
- Alpine:v3.8: `binutils` — affected >=0 <2.30-r6

## Details
In the coff_pointerize_aux function in coffgen.c in the Binary File Descriptor (BFD) library (aka libbfd), as distributed in GNU Binutils 2.30, an index is not validated, which allows remote attackers to cause a denial of service (segmentation fault) or possibly have unspecified other impact via a crafted file, as demonstrated by objcopy of a COFF object.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-7208
