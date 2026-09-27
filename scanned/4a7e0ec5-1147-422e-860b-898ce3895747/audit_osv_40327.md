# [H] net: ena: PHC: Fix potential use-after-free in get_timestamp

## Summary
Severity: High
Advisory: CVE-2026-52971
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-52971
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.17.0 <6.18.33, >=6.19.0 <7.0.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: ena: PHC: Fix potential use-after-free in get_timestamp

Move the phc->active check and resp pointer assignment to after
acquiring the spinlock. Previously, phc->active was checked without
holding the lock, and resp was cached from ena_dev->phc.virt_addr
before the lock was acquired.

If ena_com_phc_destroy() runs between the lockless active check and
the lock acquisition, it sets active=false, releases the lock, frees
the DMA memory, and sets virt_addr=NULL. The get_timestamp path would
then read a NULL virt_addr and dereference it.

With both the active check and the pointer read under the lock,
destroy cannot free the memory while get_timestamp is using it.

## References
- https://git.kernel.org/stable/c/95e8ae9af2a61b4e72f5c585bf4c7d8aaf2a2c98
- https://git.kernel.org/stable/c/ca9ed40f28949353911dcb524ff8fff2f3409c97
- https://git.kernel.org/stable/c/e42c755582f0960e684298762f0ab927b3778376
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/52xxx/CVE-2026-52971.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-52971
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
