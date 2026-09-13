# [H] Bluetooth: hci_sync: fix race in hci_cmd_sync_dequeue_once

## Summary
Severity: High
Advisory: CVE-2025-40318
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-08
Source: https://osv.dev/vulnerability/CVE-2025-40318
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.1.159, >=6.2.0 <6.6.117, >=6.7.0 <6.12.58, >=6.9.0 <6.17.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: hci_sync: fix race in hci_cmd_sync_dequeue_once

hci_cmd_sync_dequeue_once() does lookup and then cancel
the entry under two separate lock sections. Meanwhile,
hci_cmd_sync_work() can also delete the same entry,
leading to double list_del() and "UAF".

Fix this by holding cmd_sync_work_lock across both
lookup and cancel, so that the entry cannot be removed
concurrently.

## References
- https://git.kernel.org/stable/c/09b0cd1297b4dbfe736aeaa0ceeab2265f47f772
- https://git.kernel.org/stable/c/0a94f7e017438935c09ef833a1aa908ad9875213
- https://git.kernel.org/stable/c/932c0a4f77ac13e526fdd5b42914d29c9821d389
- https://git.kernel.org/stable/c/9cd536970192b72257afcdfba0bfc09993e6f19c
- https://git.kernel.org/stable/c/ae76cf6c2c842944c6514c57df54d728f1916553
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40318.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-40318
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
