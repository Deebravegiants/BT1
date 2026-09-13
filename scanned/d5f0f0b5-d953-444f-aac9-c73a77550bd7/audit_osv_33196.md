# [M] ceph: fix crash after fscrypt_encrypt_pagecache_blocks() error

## Summary
Severity: Medium
Advisory: CVE-2025-39878
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-23
Source: https://osv.dev/vulnerability/CVE-2025-39878
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.15.0 <6.16.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

ceph: fix crash after fscrypt_encrypt_pagecache_blocks() error

The function move_dirty_folio_in_page_array() was created by commit
ce80b76dd327 ("ceph: introduce ceph_process_folio_batch() method") by
moving code from ceph_writepages_start() to this function.

This new function is supposed to return an error code which is checked
by the caller (now ceph_process_folio_batch()), and on error, the
caller invokes redirty_page_for_writepage() and then breaks from the
loop.

However, the refactoring commit has gone wrong, and it by accident, it
always returns 0 (= success) because it first NULLs the pointer and
then returns PTR_ERR(NULL) which is always 0.  This means errors are
silently ignored, leaving NULL entries in the page array, which may
later crash the kernel.

The simple solution is to call PTR_ERR() before clearing the pointer.

## References
- https://git.kernel.org/stable/c/249e0a47cdb46bb9eae65511c569044bd8698d7d
- https://git.kernel.org/stable/c/dd1616ecbea920d228c56729461ed223cc501425
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39878.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39878
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
