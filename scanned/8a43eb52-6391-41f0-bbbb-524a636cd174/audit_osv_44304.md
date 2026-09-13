# [H] Bluetooth: ISO: fix use-after-free of listener socket in iso_conn_ready

## Summary
Severity: High
Advisory: CVE-2026-80914
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-09-09
Source: https://osv.dev/vulnerability/CVE-2026-80914
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.0.0 <6.12.109, >=6.13.0 <6.18.50, >=6.19.0 <7.2.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: ISO: fix use-after-free of listener socket in iso_conn_ready

iso_conn_ready() looks up the BIS listener socket with iso_get_sock(),
which takes a reference, and then, without re-checking its state,
creates a child socket from it:

    parent = iso_get_sock(hdev, ...);
    if (!parent)
        return;

    lock_sock(parent);
    sk = iso_sock_alloc(sock_net(parent), NULL, BTPROTO_ISO, ...);
    ...
    iso_chan_add(conn, sk, parent);
    ...
    release_sock(parent);
    sock_put(parent);

If the listener socket is closed concurrently, between iso_get_sock()
and lock_sock(), the reference taken by iso_get_sock() may be the last
one: the close path drops the link-list reference, and once
iso_conn_ready() drops its own reference at the end of the function the
socket is freed.  The child socket, however, is already linked to the
freed parent, and a later disconnect of the child runs iso_chan_del()
-> bt_accept_unlink(), which dereferences the dangling parent pointer
into the freed accept queue (a use-after-free).  The same dangling
pointer is also dereferenced through parent->***() in
iso_chan_del().

Fix it the same way the connected (non-BIS) path was fixed in commit
0d255e63fcf3 ("Bluetooth: ISO: hold sk properly in iso_conn_ready"):
after taking the socket lock, re-check that the parent is still a
listening, alive socket, and bail out otherwise.

## References
- https://git.kernel.org/stable/c/03288b7447c9e572f8ab82fc29cfb4ca719ab210
- https://git.kernel.org/stable/c/2387cd06a2c0b416f05028b02bba1089f54c28d9
- https://git.kernel.org/stable/c/49fd7116f76b860b230843700fb7423ab5331e1f
- https://git.kernel.org/stable/c/560bef609fa5992745929e8d7d458b9d88dd2830
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80914.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80914
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
