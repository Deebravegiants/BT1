# [H] bluetooth/hci: disallow setting handle bigger than HCI_CONN_HANDLE_MAX

## Summary
Severity: High
Advisory: CVE-2024-42132
Ecosystem: Linux
CVSS: 7.6 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:H)
Published: 2024-07-30
Source: https://osv.dev/vulnerability/CVE-2024-42132
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.6.39, >=6.7.0 <6.9.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

bluetooth/hci: disallow setting handle bigger than HCI_CONN_HANDLE_MAX

Syzbot hit warning in hci_conn_del() caused by freeing handle that was
not allocated using ida allocator.

This is caused by handle bigger than HCI_CONN_HANDLE_MAX passed by
hci_le_big_sync_established_evt(), which makes code think it's unset
connection.

Add same check for handle upper bound as in hci_conn_set_handle() to
prevent warning.

## References
- https://git.kernel.org/stable/c/1cc18c2ab2e8c54c355ea7c0423a636e415a0c23
- https://git.kernel.org/stable/c/2ae8d7742a09c275872e670c53337b3dcedaa11c
- https://git.kernel.org/stable/c/4970e48f83dbd21d2a6a7cdaaafc2a71f7f45dc4
- https://git.kernel.org/stable/c/d311036696fed778301d08a71a4bef737b86d8c5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/42xxx/CVE-2024-42132.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-42132
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
