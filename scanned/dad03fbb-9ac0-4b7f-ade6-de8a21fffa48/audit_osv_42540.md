# [H] Bluetooth: mgmt: hold reference for hci_conn in mgmt_pending_cmds

## Summary
Severity: High
Advisory: CVE-2026-68391
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68391
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.0.0 <6.6.148, >=6.7.0 <6.12.101, >=6.13.0 <6.18.42, >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: mgmt: hold reference for hci_conn in mgmt_pending_cmds

Dereferencing RCU-protected pointers outside critical sections is
invalid and may lead to UAF.  Use of hci_conn in hci_sync callbacks also
needs to hold refcount to avoid UAF.

Take appropriate locks for hci_conn lookups, and take refcount for
hci_conn pointers stored in mgmt_pending_cmd so that the pointer stays
valid.

When accessing conn->state, ensure hdev->lock is held to avoid data
race.

## References
- https://git.kernel.org/stable/c/b56f2ecafc08f372bf0529f9c4f3f429cb1702dc
- https://git.kernel.org/stable/c/d5b3b484b62bb0f4542e7622789d28871626cdf0
- https://git.kernel.org/stable/c/da55f570191d5d72f10c607a7043b947eb05ea46
- https://git.kernel.org/stable/c/ecdcb55ea1c01dda074406f38058785a69526734
- https://git.kernel.org/stable/c/f915e74b6f18293d1d69a2a3305ef321ff7c0172
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68391.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68391
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
