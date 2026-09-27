# [H] Bluetooth: ISO: clear iso_data always when detaching conn from hcon

## Summary
Severity: High
Advisory: CVE-2026-74541
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74541
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.6.0 <6.6.151, >=6.7.0 <6.12.103, >=6.13.0 <6.18.44, >=6.19.0 <7.1.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: ISO: clear iso_data always when detaching conn from hcon

When setting conn->hcon = NULL, also conn->hcon->iso_data = NULL is
necessary, otherwise later iso_conn_free() will UAF.

Fix clearing of iso_data in iso_sock_disconn()

Fixes KASAN: slab-use-after-free in iso_conn_hold_unless_zero on
iso_sock_release() followed by hci_abort_conn_sync().

## References
- https://git.kernel.org/stable/c/63c0f396a18b767eb28e895eb95bbdce6c172c59
- https://git.kernel.org/stable/c/69a4a7b162b3db6ac337e3094cdee38f24d42ff7
- https://git.kernel.org/stable/c/7b51a9c25e9698b64df9f2218f10eecf7dc7e2d0
- https://git.kernel.org/stable/c/cc1d39946d62bc568551dfb81149724de1e91338
- https://git.kernel.org/stable/c/d57e506f6a1e3929611340fae87c1e4823f4d85c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74541.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74541
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
