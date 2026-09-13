# [H] Bluetooth: L2CAP: use chan timer to close channels in cleanup_listen()

## Summary
Severity: High
Advisory: CVE-2026-53358
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-02
Source: https://osv.dev/vulnerability/CVE-2026-53358
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.4.0 <5.10.259, >=5.11.0 <5.15.210, >=5.16.0 <6.1.176, >=6.2.0 <6.6.143, >=6.7.0 <6.12.93, >=6.13.0 <6.18.35, >=6.19.0 <7.0.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: L2CAP: use chan timer to close channels in cleanup_listen()

l2cap_chan_close() removes the channel from conn->chan_l, which
must be done under conn->lock.  cleanup_listen() runs under the
parent sk_lock, so acquiring conn->lock would invert the
established conn->lock -> chan->lock -> sk_lock order.

Instead of calling l2cap_chan_close() directly, schedule
l2cap_chan_timeout with delay 0 to close the channel
asynchronously.  The timeout handler already acquires conn->lock
and chan->lock in the correct order.

The timer is only armed when chan->conn is still set: if it is
already NULL, l2cap_conn_del() has already processed this channel
(l2cap_chan_del + l2cap_sock_teardown_cb + l2cap_sock_close_cb),
so there is nothing left to do.  If l2cap_conn_del() races in
after the timer is armed, __clear_chan_timer() inside
l2cap_chan_del() cancels it; if the timer has already fired, the
handler returns harmlessly because chan->conn was cleared.

## References
- https://git.kernel.org/stable/c/3634cbdc2eb414b69ffa752ddbe5e0458518e321
- https://git.kernel.org/stable/c/50dfec218808b148ab4247b1858031b7a32015c5
- https://git.kernel.org/stable/c/7555fd885a0603f50e49a655850a1f2bd8a25398
- https://git.kernel.org/stable/c/859d3ace791ed878ae9ba5522c7844d960da8f88
- https://git.kernel.org/stable/c/89dec92041717b027216e110599e4f6d6c921b79
- https://git.kernel.org/stable/c/8c8e620467a7b51562dbcefbd1f09f288d7d710d
- https://git.kernel.org/stable/c/deb8493a8fa599f6c95e2465b12bfdfb7f94a1d9
- https://git.kernel.org/stable/c/e1c100e2d61bd8c718b7d91fe3e050780a9bf72d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53358.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53358
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
