# [H] mm: use aligned address in clear_gigantic_page()

## Summary
Severity: High
Advisory: CVE-2024-52319
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-01-11
Source: https://osv.dev/vulnerability/CVE-2024-52319
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.11.0 <6.12.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

mm: use aligned address in clear_gigantic_page()

In current kernel, hugetlb_no_page() calls folio_zero_user() with the
fault address.  Where the fault address may be not aligned with the huge
page size.  Then, folio_zero_user() may call clear_gigantic_page() with
the address, while clear_gigantic_page() requires the address to be huge
page size aligned.  So, this may cause memory corruption or information
leak, addtional, use more obvious naming 'addr_hint' instead of 'addr' for
clear_gigantic_page().

## References
- https://git.kernel.org/stable/c/8aca2bc96c833ba695ede7a45ad7784c836a262e
- https://git.kernel.org/stable/c/b79b6fe0737f233f0be1465052b7f0e75f324735
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/52xxx/CVE-2024-52319.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-52319
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
