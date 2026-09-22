# [H] Bluetooth: hci_sync: hold conn in hci_connect_acl/le_sync() callbacks

## Summary
Severity: High
Advisory: CVE-2026-80692
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-28
Source: https://osv.dev/vulnerability/CVE-2026-80692
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.9.0 <7.1.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: hci_sync: hold conn in hci_connect_acl/le_sync() callbacks

There is theoretical UAF if the conn is freed while the hci_sync task
is running.

Hold refcount to avoid that.

## References
- https://git.kernel.org/stable/c/2f5d635ad5906b0235bc0c870e8beba3116e1e98
- https://git.kernel.org/stable/c/9a77f296aff4b2ca5f2928ab3a3220c82d8b4074
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80692.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80692
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
