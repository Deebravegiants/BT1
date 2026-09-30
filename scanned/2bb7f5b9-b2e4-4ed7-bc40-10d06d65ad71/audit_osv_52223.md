# [M] CVE-2021-47214

## Summary
Severity: Medium
Advisory: CVE-2021-47214
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-04-10
Source: https://osv.dev/vulnerability/CVE-2021-47214
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

hugetlb, userfaultfd: fix reservation restore on userfaultfd error

Currently in the is_continue case in hugetlb_mcopy_atomic_pte(), if we
bail out using "goto out_release_unlock;" in the cases where idx >=
size, or !huge_pte_none(), the code will detect that new_pagecache_page
== false, and so call restore_reserve_on_error().  In this case I see
restore_reserve_on_error() delete the reservation, and the following
call to remove_inode_hugepages() will increment h->resv_hugepages
causing a 100% reproducible leak.

We should treat the is_continue case similar to adding a page into the
pagecache and set new_pagecache_page to true, to indicate that there is
no reservation to restore on the error path, and we need not call
restore_reserve_on_error().  Rename new_pagecache_page to
page_in_pagecache to make that clear.

## References
- https://git.kernel.org/stable/c/b5069d44e2fbc4a9093d005b3ef0949add3dd27e
- https://git.kernel.org/stable/c/cc30042df6fcc82ea18acf0dace831503e60a0b7
