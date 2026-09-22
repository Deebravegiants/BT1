# [H] ALPINE-CVE-2018-6543

## Summary
Severity: High
Advisory: ALPINE-CVE-2018-6543
Ecosystem: Alpine:v3.7, Alpine:v3.8
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-02-02
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-6543
Type: osv

## Affected
- Alpine:v3.7: `binutils` — affected >=0 <2.30-r2
- Alpine:v3.8: `binutils` — affected >=0 <2.30-r6

## Details
In GNU Binutils 2.30, there's an integer overflow in the function load_specific_debug_section() in objdump.c, which results in `malloc()` with 0 size. A crafted ELF file allows remote attackers to cause a denial of service (application crash) or possibly have unspecified other impact.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-6543
