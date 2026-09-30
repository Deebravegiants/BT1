# [M] CVE-2023-1583

## Summary
Severity: Medium
Advisory: CVE-2023-1583
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-03-24
Source: https://osv.dev/vulnerability/CVE-2023-1583
Type: osv

## Details
A NULL pointer dereference was found in io_file_bitmap_get in io_uring/filetable.c in the io_uring sub-component in the Linux Kernel. When fixed files are unregistered, some context information (file_alloc_{start,end} and alloc_hint) is not cleared. A subsequent request that has auto index selection enabled via IORING_FILE_INDEX_ALLOC can cause a NULL pointer dereference. An unprivileged user can use the flaw to cause a system crash.

## References
- https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=02a4d923e4400a36d340ea12d8058f69ebf3a383
- https://git.kernel.org/pub/scm/linux/kernel/git/axboe/linux-block.git/commit/?h=io_uring-6.3&id=761efd55a0227aca3a69deacdaa112fffd44fe37
