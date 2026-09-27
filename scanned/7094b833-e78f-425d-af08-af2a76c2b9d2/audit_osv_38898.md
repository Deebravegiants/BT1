# [H] Bluetooth: SCO: fix race conditions in sco_sock_connect()

## Summary
Severity: High
Advisory: CVE-2026-43023
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-01
Source: https://osv.dev/vulnerability/CVE-2026-43023
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.1.168, >=6.2.0 <6.6.134, >=6.3.0 <6.12.81, >=6.7.0 <6.18.22, >=6.13.0 <6.19.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: SCO: fix race conditions in sco_sock_connect()

sco_sock_connect() checks sk_state and sk_type without holding
the socket lock. Two concurrent connect() syscalls on the same
socket can both pass the check and enter sco_connect(), leading
to use-after-free.

The buggy scenario involves three participants and was confirmed
with additional logging instrumentation:

  Thread A (connect):    HCI disconnect:      Thread B (connect):

  sco_sock_connect(sk)                        sco_sock_connect(sk)
  sk_state==BT_OPEN                           sk_state==BT_OPEN
  (pass, no lock)                             (pass, no lock)
  sco_connect(sk):                            sco_connect(sk):
    hci_dev_lock                                hci_dev_lock
    hci_connect_sco                               <- blocked
      -> hcon1
    sco_conn_add->conn1
    lock_sock(sk)
    sco_chan_add:
      conn1->sk = sk
      sk->conn = conn1
    sk_state=BT_CONNECT
    release_sock
    hci_dev_unlock
                           hci_dev_lock
                           sco_conn_del:
                             lock_sock(sk)
                             sco_chan_del:
                               sk->conn=NULL
                               conn1->sk=NULL
                               sk_state=
                                 BT_CLOSED
                               SOCK_ZAPPED
                             release_sock
                           hci_dev_unlock
                                                  (unblocked)
                                                  hci_connect_sco
                                                    -> hcon2
                                                  sco_conn_add
                                                    -> conn2
                                                  lock_sock(sk)
                                                  sco_chan_add:
                                                    sk->conn=conn2
                                                  sk_state=
                                                    BT_CONNECT
                                                  // zombie sk!
                                                  release_sock
                                                  hci_dev_unlock

Thread B revives a BT_CLOSED + SOCK_ZAPPED socket back to
BT_CONNECT. Subsequent cleanup triggers double sock_put() and
use-after-free. Meanwhile conn1 is leaked as it was orphaned
when sco_conn_del() cleared the association.

Fix this by:
- Moving lock_sock() before the sk_state/sk_type checks in
  sco_sock_connect() to serialize concurrent connect attempts
- Fixing the sk_type != SOCK_SEQPACKET check to actually
  return the error instead of just assigning it
- Adding a state re-check in sco_connect() after lock_sock()
  to catch state changes during the window between the locks
- Adding sco_pi(sk)->conn check in sco_chan_add() to prevent
  double-attach of a socket to multiple connections
- Adding hci_conn_drop() on sco_chan_add failure to prevent
  HCI connection leaks

## References
- https://git.kernel.org/stable/c/7e296ffdab5bdab718dff7c14288fdcb9154fa27
- https://git.kernel.org/stable/c/8a5b0135d4a5d9683203a3d9a12a711ccec5936b
- https://git.kernel.org/stable/c/98c8d3bfdaa657d8f472dbbebd7ea8cd816d8a8d
- https://git.kernel.org/stable/c/adb90cd0f9f7a8d438fcb93354040fbafc5ae2a0
- https://git.kernel.org/stable/c/d002bd11024bd231bcb606877e33951ffb7bed14
- https://git.kernel.org/stable/c/dabf22269242e2f2bf44c43fcdc2fa763df7f9cc
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43023.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43023
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
