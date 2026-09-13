# [H] Bluetooth: ISO: fix iso_conn related locking and validity issues

## Summary
Severity: High
Advisory: CVE-2023-54164
Ecosystem: Linux
CVSS: 8.0 (CVSS:3.1/AV:A/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-30
Source: https://osv.dev/vulnerability/CVE-2023-54164
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.1.42, >=6.2.0 <6.4.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: ISO: fix iso_conn related locking and validity issues

sk->sk_state indicates whether iso_pi(sk)->conn is valid. Operations
that check/update sk_state and access conn should hold lock_sock,
otherwise they can race.

The order of taking locks is hci_dev_lock > lock_sock > iso_conn_lock,
which is how it is in connect/disconnect_cfm -> iso_conn_del ->
iso_chan_del.

Fix locking in iso_connect_cis/bis and sendmsg/recvmsg to take lock_sock
around updating sk_state and conn.

iso_conn_del must not occur during iso_connect_cis/bis, as it frees the
iso_conn. Hold hdev->lock longer to prevent that.

This should not reintroduce the issue fixed in commit 241f51931c35
("Bluetooth: ISO: Avoid circular locking dependency"), since the we
acquire locks in order. We retain the fix in iso_sock_connect to release
lock_sock before iso_connect_* acquires hdev->lock.

Similarly for commit 6a5ad251b7cd ("Bluetooth: ISO: Fix possible
circular locking dependency"). We retain the fix in iso_conn_ready to
not acquire iso_conn_lock before lock_sock.

iso_conn_add shall return iso_conn with valid hcon. Make it so also when
reusing an old CIS connection waiting for disconnect timeout (see
__iso_sock_close where conn->hcon is set to NULL).

Trace with iso_conn_del after iso_chan_add in iso_connect_cis:
===============================================================
iso_sock_create:771: sock 00000000be9b69b7
iso_sock_init:693: sk 000000004dff667e
iso_sock_bind:827: sk 000000004dff667e 70:1a:b8:98:ff:a2 type 1
iso_sock_setsockopt:1289: sk 000000004dff667e
iso_sock_setsockopt:1289: sk 000000004dff667e
iso_sock_setsockopt:1289: sk 000000004dff667e
iso_sock_connect:875: sk 000000004dff667e
iso_connect_cis:353: 70:1a:b8:98:ff:a2 -> 28:3d:c2:4a:7e:da
hci_get_route:1199: 70:1a:b8:98:ff:a2 -> 28:3d:c2:4a:7e:da
hci_conn_add:1005: hci0 dst 28:3d:c2:4a:7e:da
iso_conn_add:140: hcon 000000007b65d182 conn 00000000daf8625e
__iso_chan_add:214: conn 00000000daf8625e
iso_connect_cfm:1700: hcon 000000007b65d182 bdaddr 28:3d:c2:4a:7e:da status 12
iso_conn_del:187: hcon 000000007b65d182 conn 00000000daf8625e, err 16
iso_sock_clear_timer:117: sock 000000004dff667e state 3
    <Note: sk_state is BT_BOUND (3), so iso_connect_cis is still
    running at this point>
iso_chan_del:153: sk 000000004dff667e, conn 00000000daf8625e, err 16
hci_conn_del:1151: hci0 hcon 000000007b65d182 handle 65535
hci_conn_unlink:1102: hci0: hcon 000000007b65d182
hci_chan_list_flush:2780: hcon 000000007b65d182
iso_sock_getsockopt:1376: sk 000000004dff667e
iso_sock_getname:1070: sock 00000000be9b69b7, sk 000000004dff667e
iso_sock_getname:1070: sock 00000000be9b69b7, sk 000000004dff667e
iso_sock_getsockopt:1376: sk 000000004dff667e
iso_sock_getname:1070: sock 00000000be9b69b7, sk 000000004dff667e
iso_sock_getname:1070: sock 00000000be9b69b7, sk 000000004dff667e
iso_sock_shutdown:1434: sock 00000000be9b69b7, sk 000000004dff667e, how 1
__iso_sock_close:632: sk 000000004dff667e state 5 socket 00000000be9b69b7
     <Note: sk_state is BT_CONNECT (5), even though iso_chan_del sets
     BT_CLOSED (6). Only iso_connect_cis sets it to BT_CONNECT, so it
     must be that iso_chan_del occurred between iso_chan_add and end of
     iso_connect_cis.>
BUG: kernel NULL pointer dereference, address: 0000000000000000
PGD 8000000006467067 P4D 8000000006467067 PUD 3f5f067 PMD 0
Oops: 0000 [#1] PREEMPT SMP PTI
Hardware name: QEMU Standard PC (Q35 + ICH9, 2009), BIOS 1.16.2-1.fc38 04/01/2014
RIP: 0010:__iso_sock_close (net/bluetooth/iso.c:664) bluetooth
===============================================================

Trace with iso_conn_del before iso_chan_add in iso_connect_cis:
===============================================================
iso_connect_cis:356: 70:1a:b8:98:ff:a2 -> 28:3d:c2:4a:7e:da
...
iso_conn_add:140: hcon 0000000093bc551f conn 00000000768ae504
hci_dev_put:1487: hci0 orig refcnt 21
hci_event_packet:7607: hci0: e
---truncated---

## References
- https://git.kernel.org/stable/c/88ad50f2b843a510bd7c922c0a4e2484aff9d645
- https://git.kernel.org/stable/c/d40ae85ee62e3666f45bc61864b22121346f88ef
- https://git.kernel.org/stable/c/e969bfed84c1f88dc722a678ee08488e86f0ec1a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/54xxx/CVE-2023-54164.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-54164
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
