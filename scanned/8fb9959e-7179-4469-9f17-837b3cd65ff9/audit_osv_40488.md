# [H] Bluetooth: fix UAF in l2cap_sock_cleanup_listen() vs l2cap_conn_del()

## Summary
Severity: High
Advisory: CVE-2026-53357
Ecosystem: Linux
CVSS: 8.0 (CVSS:3.1/AV:A/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-02
Source: https://osv.dev/vulnerability/CVE-2026-53357
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.7.0 <5.10.259, >=5.11.0 <5.15.210, >=5.16.0 <6.1.175, >=6.2.0 <6.6.142, >=6.7.0 <6.12.92, >=6.13.0 <6.18.34, >=6.19.0 <7.0.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: fix UAF in l2cap_sock_cleanup_listen() vs l2cap_conn_del()

bt_accept_dequeue() unlinks a not-yet-accepted child from the parent
accept queue and release_sock()s it before returning, so the returned
sk has no caller reference and is unlocked.

l2cap_sock_cleanup_listen() walks these children on listening-socket
close.  A concurrent HCI disconnect drives hci_rx_work ->
l2cap_conn_del() which runs l2cap_chan_del() + l2cap_sock_kill() and
frees the child sk and its l2cap_chan; cleanup_listen() then uses both:

  BUG: KASAN: slab-use-after-free in l2cap_sock_kill
    l2cap_sock_kill / l2cap_sock_cleanup_listen / __x64_sys_close
  Freed by: l2cap_conn_del -> l2cap_sock_close_cb -> l2cap_sock_kill

This is distinct from the two fixes already in this area: commit
e83f5e24da741 ("Bluetooth: serialize accept_q access") serialises the
accept_q list/poll and takes temporary refs inside bt_accept_dequeue(),
and CVE-2025-39860 serialises the userspace close()/accept() race by
calling cleanup_listen() under lock_sock() in l2cap_sock_release().
Neither covers l2cap_conn_del() running from hci_rx_work, so this UAF
still reproduces on current bluetooth/master.

Take the reference at the source: bt_accept_dequeue() does sock_hold()
while sk is still locked, before release_sock(); callers sock_put().
cleanup_listen() pins the chan with l2cap_chan_hold_unless_zero() under
a brief child sk lock (serialising vs l2cap_sock_teardown_cb()), drops
it before l2cap_chan_lock(), and skips a duplicate l2cap_sock_kill() on
SOCK_DEAD.  conn->lock is not taken here: cleanup_listen() runs under
the parent sk lock and that would invert
conn->lock -> chan->lock -> sk_lock (lockdep).

KASAN/SMP: an unprivileged listen/close vs HCI-disconnect race produced
12 use-after-free reports per run before this change; 0, and no lockdep
report, over 1600+ raced iterations after it on bluetooth/master.

## References
- https://git.kernel.org/stable/c/407217734835d21d4e0105ebf347860dc1806f88
- https://git.kernel.org/stable/c/5d86d2f1b4d9a508c441d3e45277ae1a73cfed57
- https://git.kernel.org/stable/c/751de6ec671fe75ad9cf65a0638d2a06b6a5984d
- https://git.kernel.org/stable/c/7eebd4c2c86f573af87ff165d08a83432eb0b919
- https://git.kernel.org/stable/c/87c543e2f78d0871f271df92dab98901bbd5b6f5
- https://git.kernel.org/stable/c/a5ca86a6097a8b030ca3226cd300b17ed330f966
- https://git.kernel.org/stable/c/ab1513597c6cf17cd1ad2a21e3b045421b48e022
- https://git.kernel.org/stable/c/added1213395071470a900cc845a042fb51882a6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53357.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53357
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
