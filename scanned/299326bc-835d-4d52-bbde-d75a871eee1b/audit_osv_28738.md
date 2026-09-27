# [H] Bluetooth: msft: fix slab-use-after-free in msft_do_close()

## Summary
Severity: High
Advisory: CVE-2024-36012
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-23
Source: https://osv.dev/vulnerability/CVE-2024-36012
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.12.0 <6.1.91, >=6.2.0 <6.6.31, >=6.7.0 <6.8.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: msft: fix slab-use-after-free in msft_do_close()

Tying the msft->data lifetime to hdev by freeing it in
hci_release_dev() to fix the following case:

[use]
msft_do_close()
  msft = hdev->msft_data;
  if (!msft)                      ...(1) <- passed.
    return;
  mutex_lock(&msft->filter_lock); ...(4) <- used after freed.

[free]
msft_unregister()
  msft = hdev->msft_data;
  hdev->msft_data = NULL;         ...(2)
  kfree(msft);                    ...(3) <- msft is freed.

==================================================================
BUG: KASAN: slab-use-after-free in __mutex_lock_common
kernel/locking/mutex.c:587 [inline]
BUG: KASAN: slab-use-after-free in __mutex_lock+0x8f/0xc30
kernel/locking/mutex.c:752
Read of size 8 at addr ffff888106cbbca8 by task kworker/u5:2/309

## References
- https://git.kernel.org/stable/c/10f9f426ac6e752c8d87bf4346930ba347aaabac
- https://git.kernel.org/stable/c/4f1de02de07748da80a8178879bc7a1df37fdf56
- https://git.kernel.org/stable/c/a85a60e62355e3bf4802dead7938966824b23940
- https://git.kernel.org/stable/c/e3880b531b68f98d3941d83f2f6dd11cf4fd6b76
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/36xxx/CVE-2024-36012.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-36012
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
