# [H] Bluetooth: hci_sync: hold conn in hci_connect_pa_sync() callback

## Summary
Severity: High
Advisory: CVE-2026-74529
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74529
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.15.0 <7.1.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: hci_sync: hold conn in hci_connect_pa_sync() callback

There is theoretical UAF if the conn is freed while the hci_sync task is
running.

Hold refcount to avoid that.

## References
- https://git.kernel.org/stable/c/44fc74069d8988f2825246f9401218e29de2c0ab
- https://git.kernel.org/stable/c/c53c70ec289ee12f20c4f1b2fbfd151762c01f67
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74529.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74529
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
