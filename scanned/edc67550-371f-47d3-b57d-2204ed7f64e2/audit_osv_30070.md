# [H] Bluetooth: MGMT: Fix possible crash on mgmt_index_removed

## Summary
Severity: High
Advisory: CVE-2024-49951
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-10-21
Source: https://osv.dev/vulnerability/CVE-2024-49951
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.0.0 <6.1.120, >=6.2.0 <6.6.55, >=6.7.0 <6.10.14, >=6.11.0 <6.11.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: MGMT: Fix possible crash on mgmt_index_removed

If mgmt_index_removed is called while there are commands queued on
cmd_sync it could lead to crashes like the bellow trace:

0x0000053D: __list_del_entry_valid_or_report+0x98/0xdc
0x0000053D: mgmt_pending_remove+0x18/0x58 [bluetooth]
0x0000053E: mgmt_remove_adv_monitor_complete+0x80/0x108 [bluetooth]
0x0000053E: hci_cmd_sync_work+0xbc/0x164 [bluetooth]

So while handling mgmt_index_removed this attempts to dequeue
commands passed as user_data to cmd_sync.

## References
- https://git.kernel.org/stable/c/0cc47233af35fb5f10b5e6a027cb4ccd480caf9a
- https://git.kernel.org/stable/c/19b40ca62607cef78369549d1af091f2fd558931
- https://git.kernel.org/stable/c/4883296505aa7e4863c6869b689afb6005633b23
- https://git.kernel.org/stable/c/8c3f7943a29145d8a2d8e24893762f7673323eae
- https://git.kernel.org/stable/c/f53e1c9c726d83092167f2226f32bd3b73f26c21
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/49xxx/CVE-2024-49951.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-49951
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
