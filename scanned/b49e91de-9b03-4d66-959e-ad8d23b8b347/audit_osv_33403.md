# [H] Bluetooth: MGMT: cancel mesh send timer when hdev removed

## Summary
Severity: High
Advisory: CVE-2025-40284
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-06
Source: https://osv.dev/vulnerability/CVE-2025-40284
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.1.0 <6.1.159, >=6.2.0 <6.6.117, >=6.7.0 <6.12.59, >=6.13.0 <6.17.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: MGMT: cancel mesh send timer when hdev removed

mesh_send_done timer is not canceled when hdev is removed, which causes
crash if the timer triggers after hdev is gone.

Cancel the timer when MGMT removes the hdev, like other MGMT timers.

Should fix the BUG: sporadically seen by BlueZ test bot
(in "Mesh - Send cancel - 1" test).

Log:
------
BUG: KASAN: slab-use-after-free in run_timer_softirq+0x76b/0x7d0
...
Freed by task 36:
 kasan_save_stack+0x24/0x50
 kasan_save_track+0x14/0x30
 __kasan_save_free_info+0x3a/0x60
 __kasan_slab_free+0x43/0x70
 kfree+0x103/0x500
 device_release+0x9a/0x210
 kobject_put+0x100/0x1e0
 vhci_release+0x18b/0x240
------

## References
- https://git.kernel.org/stable/c/2927ff643607eddf4f03d10ef80fe10d977154aa
- https://git.kernel.org/stable/c/55fb52ffdd62850d667ebed842815e072d3c9961
- https://git.kernel.org/stable/c/7b6b6c077cad0601d62c3c34ab7ce3fb25deda7b
- https://git.kernel.org/stable/c/990e6143b0ca0c66f099d67d00c112bf59b30d76
- https://git.kernel.org/stable/c/fd62ca5ad136dcf6f5aa308423b299a6be6f54ea
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40284.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-40284
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
