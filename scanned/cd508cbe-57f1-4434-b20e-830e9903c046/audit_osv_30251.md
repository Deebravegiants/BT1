# [M] wifi: ath10k: Fix memory leak in management tx

## Summary
Severity: Medium
Advisory: CVE-2024-50236
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-11-09
Source: https://osv.dev/vulnerability/CVE-2024-50236
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.19.0 <4.19.323, >=4.20.0 <5.4.285, >=5.5.0 <5.10.229, >=5.11.0 <5.15.171, >=5.16.0 <6.1.116, >=6.2.0 <6.6.60, >=6.7.0 <6.11.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: ath10k: Fix memory leak in management tx

In the current logic, memory is allocated for storing the MSDU context
during management packet TX but this memory is not being freed during
management TX completion. Similar leaks are seen in the management TX
cleanup logic.

Kmemleak reports this problem as below,

unreferenced object 0xffffff80b64ed250 (size 16):
  comm "kworker/u16:7", pid 148, jiffies 4294687130 (age 714.199s)
  hex dump (first 16 bytes):
    00 2b d8 d8 80 ff ff ff c4 74 e9 fd 07 00 00 00  .+.......t......
  backtrace:
    [<ffffffe6e7b245dc>] __kmem_cache_alloc_node+0x1e4/0x2d8
    [<ffffffe6e7adde88>] kmalloc_trace+0x48/0x110
    [<ffffffe6bbd765fc>] ath10k_wmi_tlv_op_gen_mgmt_tx_send+0xd4/0x1d8 [ath10k_core]
    [<ffffffe6bbd3eed4>] ath10k_mgmt_over_wmi_tx_work+0x134/0x298 [ath10k_core]
    [<ffffffe6e78d5974>] process_scheduled_works+0x1ac/0x400
    [<ffffffe6e78d60b8>] worker_thread+0x208/0x328
    [<ffffffe6e78dc890>] kthread+0x100/0x1c0
    [<ffffffe6e78166c0>] ret_from_fork+0x10/0x20

Free the memory during completion and cleanup to fix the leak.

Protect the mgmt_pending_tx idr_remove() operation in
ath10k_wmi_tlv_op_cleanup_mgmt_tx_send() using ar->data_lock similar to
other instances.

Tested-on: WCN3990 hw1.0 SNOC WLAN.HL.2.0-01387-QCAHLSWMTPLZ-1

## References
- https://git.kernel.org/stable/c/2f6f1e26ac6d2b38e2198a71f81f0ade14d6b07b
- https://git.kernel.org/stable/c/4112450da7d67b59ccedc2208bae622db17dbcb8
- https://git.kernel.org/stable/c/5f5a939759c79e7385946c85e62feca51a18d816
- https://git.kernel.org/stable/c/6cc23898e6ba47e976050d3c080b4d2c1add3748
- https://git.kernel.org/stable/c/6fc9af3df6ca7f3c94774d20f62dc7b49616026d
- https://git.kernel.org/stable/c/705be2dc45c7f852e211e16bc41a916fab741983
- https://git.kernel.org/stable/c/e15d84b3bba187aa372dff7c58ce1fd5cb48a076
- https://git.kernel.org/stable/c/eff818238bedb9c2484c251ec46f9f160911cdc0
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50236.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50236
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
