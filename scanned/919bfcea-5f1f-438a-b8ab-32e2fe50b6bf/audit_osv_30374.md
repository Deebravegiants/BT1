# [H] mm: use aligned address in copy_user_gigantic_page()

## Summary
Severity: High
Advisory: CVE-2024-51729
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-01-11
Source: https://osv.dev/vulnerability/CVE-2024-51729
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.11.0 <6.12.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

mm: use aligned address in copy_user_gigantic_page()

In current kernel, hugetlb_wp() calls copy_user_large_folio() with the
fault address.  Where the fault address may be not aligned with the huge
page size.  Then, copy_user_large_folio() may call
copy_user_gigantic_page() with the address, while
copy_user_gigantic_page() requires the address to be huge page size
aligned.  So, this may cause memory corruption or information leak,
addtional, use more obvious naming 'addr_hint' instead of 'addr' for
copy_user_gigantic_page().

## References
- https://git.kernel.org/stable/c/cb12d61361ce769672c7c7bd32107252598cdd8b
- https://git.kernel.org/stable/c/f5d09de9f1bf9674c6418ff10d0a40cfe29268e1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/51xxx/CVE-2024-51729.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-51729
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
