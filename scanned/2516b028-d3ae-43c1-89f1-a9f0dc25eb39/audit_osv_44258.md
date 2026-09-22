# [H] Bluetooth: SCO: give the socket its own sco_conn reference

## Summary
Severity: High
Advisory: CVE-2026-80683
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-28
Source: https://osv.dev/vulnerability/CVE-2026-80683
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.13.0 <6.18.44, >=6.19.0 <7.1.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: SCO: give the socket its own sco_conn reference

sco_conn_del() drops a reference it does not own. It takes one transient
reference via sco_conn_hold_unless_zero() and releases it with the
sco_conn_put() that follows sco_sock_hold(); the additional put in the
!sk branch releases a second one:

    conn = sco_conn_hold_unless_zero(conn);
    ...
    sk = sco_sock_hold(conn);
    sco_conn_unlock(conn);
    sco_conn_put(conn);

    if (!sk) {
            sco_conn_put(conn);
            return;
    }

When close() races the controller's Disconnection Complete, sco_chan_del()
clears conn->sk and drops the socket's reference while sco_conn_del() is
running. sco_conn_del() then sees sk == NULL, its own put drops the count
to zero and frees the conn, and the second put writes to the freed kref:

    BUG: KASAN: slab-use-after-free in sco_conn_put.part.0+0x1a/0x190
    Write of size 4 at addr ffff8881099dec74 by task kworker/u17:3/413
    Workqueue: hci1 hci_rx_work
    Call Trace:
     sco_conn_put.part.0+0x1a/0x190
     hci_disconn_complete_evt+0x1ee/0x3e0
     hci_event_packet+0x54a/0x650
     hci_rx_work+0x321/0x3d0
    Allocated by task 413:
     sco_conn_add+0x72/0x1a0
     sco_connect_cfm+0x88/0x670
    Freed by task 413:
     sco_conn_del.isra.0+0x3f/0xf0
     hci_disconn_complete_evt+0x1ee/0x3e0
    refcount_t: underflow; use-after-free.

The root cause is that the socket stores the connection without holding a
reference of its own. __sco_chan_add() does:

    sco_pi(sk)->conn = conn;

so the socket borrows whatever reference its caller happened to hold, and
the callers paper over that with ad-hoc holds and puts. Give the socket a
counted reference instead: __sco_chan_add() takes one and it is released
together with the channel (sco_chan_del()) and in sco_sock_destruct().
With the socket holding its own reference, sco_conn_del() no longer needs
the extra put and the redundant hold in sco_conn_ready() goes away.

Making the socket own its reference means the connection is now actually
freed on the error paths of sco_connect() where it used to leak, which in
turn runs sco_conn_free() and its hci_conn_drop(conn->hcon). To keep the
hci_conn accounting balanced, make that ownership explicit as well:
sco_conn_add() consumes one hci_conn reference and the sco_conn owns it for
its lifetime. sco_connect() hands over the reference returned by
hci_connect_sco() and no longer drops it on the error paths;
sco_connect_cfm(), which is not given a reference, takes one with
hci_conn_hold() before handing it to sco_conn_add() (and drops it again if
the allocation fails); and the explicit hci_conn_hold() in sco_conn_ready()
is removed. Every reference then has a single, clear owner.

## References
- https://git.kernel.org/stable/c/8fe627192fa5da7157f9a48608f13c04b6373e43
- https://git.kernel.org/stable/c/a33bc07b4730b6cd5681ac77d18ae0de3e739690
- https://git.kernel.org/stable/c/abd93c85c8667add738ee82aeab95dd9fc8265a2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80683.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80683
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
