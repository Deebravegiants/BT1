# [M] CVE-2023-22997

## Summary
Severity: Medium
Advisory: CVE-2023-22997
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-02-28
Source: https://osv.dev/vulnerability/CVE-2023-22997
Type: osv

## Details
In the Linux kernel before 6.1.2, kernel/module/decompress.c misinterprets the module_get_next_page return value (expects it to be NULL in the error case, whereas it is actually an error pointer).

## References
- https://cdn.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.1.2
- https://github.com/torvalds/linux/commit/45af1d7aae7d5520d2858f8517a1342646f015db
