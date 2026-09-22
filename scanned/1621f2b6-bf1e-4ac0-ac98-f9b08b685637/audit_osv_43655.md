# [H] Bluetooth: ISO: avoid deadlocks in iso_sock_timeout

## Summary
Severity: High
Advisory: CVE-2026-74535
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74535
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.12.103, >=6.13.0 <7.1.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: ISO: avoid deadlocks in iso_sock_timeout

iso_sock_timeout() takes lock_sock, so sync disabling the timer while
holding that lock may deadlock.

iso_sock_timeout() may also run concurrently with iso_conn_del(), which
leads to UAF

        [Task 1]                      [Task hdev->workqueue]
        iso_sock_timeout              iso_conn_del
          iso_conn_hold_unless_zero     iso_chan_del
                           `------------> iso_conn_put
                                      caller frees hcon
          iso_conn_put
            iso_conn_free
              conn->hcon->iso_data = NULL; /* UAF */

Fix the deadlock by removing the disable from the lock_sock sections.
Move the timer from iso_conn to iso_pinfo to decouple it from iso_conn
which may need to be freed in lock_sock section. Convert some of the
clear_timer to disable_timer.

## References
- https://git.kernel.org/stable/c/16d89a63e08280abeef7218970a3bbd7ca62b021
- https://git.kernel.org/stable/c/200fa1629c57a3ca2b03d3ca63fd3a9bfd910c43
- https://git.kernel.org/stable/c/3c3d5f85db80145636bb991a6005e2760012b985
- https://git.kernel.org/stable/c/82e982f54f962f72646868ddbb2c3bd9ea178568
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74535.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74535
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
