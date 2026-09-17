# [H] Bluetooth: hci_sync: extend conn_hash lookup critical sections

## Summary
Severity: High
Advisory: CVE-2026-68393
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68393
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.15.0 <6.18.42, >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: hci_sync: extend conn_hash lookup critical sections

Using RCU-protected pointers outside the critical sections without
refcount is incorrect and may result to UAF.

Extend critical section to cover both hci_conn_hash lookup and use of
the returned conn.

Add surrounding rcu_read_lock() also when return value is not used, in
preparation for RCU lockdep requirement to hci_lookup_le_connect().

This avoids concurrent deletion of the conn before we are done
dereferencing it.

Also, make sure to hold hdev->lock when accessing hdev->accept_list.

## References
- https://git.kernel.org/stable/c/38326774df6198df0cc2744cc73bf77cb741c538
- https://git.kernel.org/stable/c/83b7e67698d0b93f685875ce82c8d335436834f7
- https://git.kernel.org/stable/c/d5efd6e4b8b0634af6843178fe1a7dd2b2178a3d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68393.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68393
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
