# [H] CVE-2021-47087

## Summary
Severity: High
Advisory: CVE-2021-47087
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-03-04
Source: https://osv.dev/vulnerability/CVE-2021-47087
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

tee: optee: Fix incorrect page free bug

Pointer to the allocated pages (struct page *page) has already
progressed towards the end of allocation. It is incorrect to perform
__free_pages(page, order) using this pointer as we would free any
arbitrary pages. Fix this by stop modifying the page pointer.

## References
- https://git.kernel.org/stable/c/91e94e42f6fc49635f1a16d8ae3f79552bcfda29
- https://git.kernel.org/stable/c/ad338d825e3f7b96ee542bf313728af2d19fe9ad
- https://git.kernel.org/stable/c/18549bf4b21c739a9def39f27dcac53e27286ab5
- https://git.kernel.org/stable/c/806142c805cacd098e61bdc0f72c778a2389fe4a
