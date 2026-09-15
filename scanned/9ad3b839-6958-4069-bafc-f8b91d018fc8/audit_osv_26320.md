# [H] nbd: fix uaf in nbd_open

## Summary
Severity: High
Advisory: CVE-2023-52837
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2023-52837
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.14.0 <6.1.63, >=6.2.0 <6.5.12, >=6.6.0 <6.6.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

nbd: fix uaf in nbd_open

Commit 4af5f2e03013 ("nbd: use blk_mq_alloc_disk and
blk_cleanup_disk") cleans up disk by blk_cleanup_disk() and it won't set
disk->private_data as NULL as before. UAF may be triggered in nbd_open()
if someone tries to open nbd device right after nbd_put() since nbd has
been free in nbd_dev_remove().

Fix this by implementing ->free_disk and free private data in it.

## References
- https://git.kernel.org/stable/c/327462725b0f759f093788dfbcb2f1fd132f956b
- https://git.kernel.org/stable/c/4e9b3ec84dc97909876641dad14e0a2300d6c2a3
- https://git.kernel.org/stable/c/56bd7901b5e9dbc9112036ea615ebcba1565fafe
- https://git.kernel.org/stable/c/879947f4180bc6e83af64eb0515e0cf57fce15db
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52837.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52837
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
