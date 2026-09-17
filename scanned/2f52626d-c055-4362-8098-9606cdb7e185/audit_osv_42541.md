# [H] Bluetooth: mgmt: fix locking in unpair_device/disconnect_sync

## Summary
Severity: High
Advisory: CVE-2026-68392
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68392
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.6.148, >=6.7.0 <6.12.101, >=6.11.0 <6.18.42, >=6.13.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: mgmt: fix locking in unpair_device/disconnect_sync

Dereferencing RCU-protected pointers outside critical sections is
invalid and may lead to UAF.

Take hdev->lock for hci_conn lookup and hci_abort_conn().  Don't use RCU
to ensure the conn is fully initialized at this point.

## References
- https://git.kernel.org/stable/c/16cd66443957e4ad42155c6fec401012f600c6f8
- https://git.kernel.org/stable/c/579faba5ede6df6b7f36777c431dc8dcf9d272e7
- https://git.kernel.org/stable/c/74f3e6e21ebc6c418d348f8ce68aef6fe6d82c82
- https://git.kernel.org/stable/c/8bc83f9ef6789571f399ff631a2a14a12b6d8585
- https://git.kernel.org/stable/c/b11511006f9e17000de3f4cadee451364f658ca3
- https://git.kernel.org/stable/c/ca58ad287bfc5b9d31a72ecb8650289df2b57250
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68392.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68392
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
