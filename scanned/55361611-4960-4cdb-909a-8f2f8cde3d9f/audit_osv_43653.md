# [H] Bluetooth: ISO: fix race of kfree vs kref_get_unless_zero

## Summary
Severity: High
Advisory: CVE-2026-74533
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74533
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.13.0 <7.1.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: ISO: fix race of kfree vs kref_get_unless_zero

hci_conn::iso_data is accessed and modified without lock or RCU.
This leads to a race

    [Task hdev->workqueue]                 	[Task 2]
    iso_recv                                    iso_conn_put(conn)
      conn = LOAD hcon->iso_data                  iso_conn_free(conn)
      iso_conn_hold_unless_zero(conn)               hcon->iso_data = NULL
                                                    kfree(conn)
        kref_get_unless_zero(&conn->ref) /* UAF */

and also to races in iso_conn_add() vs. iso_conn_free().

Fix by adding spinlock hci_conn::proto_lock and using it to guard
hci_conn::iso_data.

## References
- https://git.kernel.org/stable/c/876a3e94c70d0859d1dad1c986112d4f0d99eba8
- https://git.kernel.org/stable/c/af24e338bf5dafb80f42baa9a0b9e9b57b1c5d9c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74533.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74533
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
