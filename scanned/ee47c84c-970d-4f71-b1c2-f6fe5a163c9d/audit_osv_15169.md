# [M] CVE-2019-14248

## Summary
Severity: Medium
Advisory: CVE-2019-14248
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-07-24
Source: https://osv.dev/vulnerability/CVE-2019-14248
Type: osv

## Details
In libnasm.a in Netwide Assembler (NASM) 2.14.xx, asm/pragma.c allows a NULL pointer dereference in process_pragma, search_pragma_list, and nasm_set_limit when "%pragma limit" is mishandled.

## References
- https://bugzilla.nasm.us/show_bug.cgi?id=3392576
