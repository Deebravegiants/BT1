# [H] Bluetooth: ISO: fix refcounting of iso_conn

## Summary
Severity: High
Advisory: CVE-2026-74534
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74534
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.13.0 <6.18.44, >=6.19.0 <7.1.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: ISO: fix refcounting of iso_conn

iso_conn_del() and iso_chan_del() have a race that results to double-put
of iso_conn:

    [Task hdev->workqueue]         [Task 2]
    iso_conn_del                   iso_chan_del
      iso_conn_hold_unless_zero      iso_conn_lock
      iso_conn_lock                  conn->sk = NULL
                                     iso_conn_unlock
      sk = iso_sock_hold(conn)  <---------´
      if (!sk) iso_conn_put          iso_conn_put
      iso_conn_put /* UAF */

The extra put for !sk in iso_conn_del() is currently required since
failing iso_chan_add() may leave iso_conn not associated with any sk.

Fix by having iso_pi(sk)->conn own refcount when non-NULL, so
iso_conn_del does not need to put it.  Adjust the iso_conn_add()
refcounting so that conn is put if it does not get associated with an
sk.

## References
- https://git.kernel.org/stable/c/3b921533e8aa95b77aadcf31737595578e735f3c
- https://git.kernel.org/stable/c/8208b4939afb0a1977fffe902c3ca42fe0f3baaa
- https://git.kernel.org/stable/c/fdfde532ab1caa165fcd8985001157ac8b4db365
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74534.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74534
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
