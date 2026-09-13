# [M] CVE-2021-46924

## Summary
Severity: Medium
Advisory: CVE-2021-46924
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-02-27
Source: https://osv.dev/vulnerability/CVE-2021-46924
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

NFC: st21nfca: Fix memory leak in device probe and remove

'phy->pending_skb' is alloced when device probe, but forgot to free
in the error handling path and remove path, this cause memory leak
as follows:

unreferenced object 0xffff88800bc06800 (size 512):
  comm "8", pid 11775, jiffies 4295159829 (age 9.032s)
  hex dump (first 32 bytes):
    00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
    00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
  backtrace:
    [<00000000d66c09ce>] __kmalloc_node_track_caller+0x1ed/0x450
    [<00000000c93382b3>] kmalloc_reserve+0x37/0xd0
    [<000000005fea522c>] __alloc_skb+0x124/0x380
    [<0000000019f29f9a>] st21nfca_hci_i2c_probe+0x170/0x8f2

Fix it by freeing 'pending_skb' in error and remove.

## References
- https://git.kernel.org/stable/c/a1e0080a35a16ce3808f7040fe0c3a8fdb052349
- https://git.kernel.org/stable/c/e553265ea56482da5700f56319fda9ff53e7dcb4
- https://git.kernel.org/stable/c/1b9dadba502234eea7244879b8d5d126bfaf9f0c
- https://git.kernel.org/stable/c/1cd4063dbc91cf7965d73a6a3855e2028cd4613b
- https://git.kernel.org/stable/c/238920381b8925d070d32d73cd9ce52ab29896fe
- https://git.kernel.org/stable/c/38c3e320e7ff46f2dc67bc5045333e63d9f8918d
