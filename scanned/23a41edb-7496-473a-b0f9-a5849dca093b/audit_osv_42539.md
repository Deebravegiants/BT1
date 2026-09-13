# [H] Bluetooth: hci_sync: hold hdev->lock for hci_conn_params lookups

## Summary
Severity: High
Advisory: CVE-2026-68390
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68390
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: hci_sync: hold hdev->lock for hci_conn_params lookups

hci_conn_params_lookup requires hdev->lock be held, otherwise the list
iteration or param access is not safe.

Hold hdev->lock for params lookups in hci_sync.

## References
- https://git.kernel.org/stable/c/8d892bec1dd134761cabec6ba23fe315d0f20f98
- https://git.kernel.org/stable/c/c363202ec841df36421ec280eea3d5f94f556143
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68390.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68390
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
