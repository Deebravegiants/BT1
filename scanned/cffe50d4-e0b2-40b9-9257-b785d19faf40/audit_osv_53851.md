# [M] CVE-2023-28866

## Summary
Severity: Medium
Advisory: CVE-2023-28866
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2023-03-27
Source: https://osv.dev/vulnerability/CVE-2023-28866
Type: osv

## Details
In the Linux kernel through 6.2.8, net/bluetooth/hci_sync.c allows out-of-bounds access because amp_init1[] and amp_init2[] are supposed to have an intentionally invalid element, but do not.

## References
- https://lore.kernel.org/lkml/20230321015018.1759683-1-iam%40sung-woo.kim/
- https://patchwork.kernel.org/project/bluetooth/patch/20230322232543.3079578-1-luiz.dentz%40gmail.com
- https://git.kernel.org/pub/scm/linux/kernel/git/bluetooth/bluetooth-next.git/commit/?id=95084403f8c070ccf5d7cbe72352519c1798a40a
