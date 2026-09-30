# [M] CVE-2021-4454

## Summary
Severity: Medium
Advisory: CVE-2021-4454
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-03-27
Source: https://osv.dev/vulnerability/CVE-2021-4454
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

can: j1939: fix errant WARN_ON_ONCE in j1939_session_deactivate

The conclusion "j1939_session_deactivate() should be called with a
session ref-count of at least 2" is incorrect. In some concurrent
scenarios, j1939_session_deactivate can be called with the session
ref-count less than 2. But there is not any problem because it
will check the session active state before session putting in
j1939_session_deactivate_locked().

Here is the concurrent scenario of the problem reported by syzbot
and my reproduction log.

        cpu0                            cpu1
                                j1939_xtp_rx_eoma
j1939_xtp_rx_abort_one
                                j1939_session_get_by_addr [kref == 2]
j1939_session_get_by_addr [kref == 3]
j1939_session_deactivate [kref == 2]
j1939_session_put [kref == 1]
				j1939_session_completed
				j1939_session_deactivate
				WARN_ON_ONCE(kref < 2)

=====================================================
WARNING: CPU: 1 PID: 21 at net/can/j1939/transport.c:1088 j1939_session_deactivate+0x5f/0x70
CPU: 1 PID: 21 Comm: ksoftirqd/1 Not tainted 5.14.0-rc7+ #32
Hardware name: QEMU Standard PC (i440FX + PIIX, 1996), BIOS 1.13.0-1ubuntu1 04/01/2014
RIP: 0010:j1939_session_deactivate+0x5f/0x70
Call Trace:
 j1939_session_deactivate_activate_next+0x11/0x28
 j1939_xtp_rx_eoma+0x12a/0x180
 j1939_tp_recv+0x4a2/0x510
 j1939_can_recv+0x226/0x380
 can_rcv_filter+0xf8/0x220
 can_receive+0x102/0x220
 ? process_backlog+0xf0/0x2c0
 can_rcv+0x53/0xf0
 __netif_receive_skb_one_core+0x67/0x90
 ? process_backlog+0x97/0x2c0
 __netif_receive_skb+0x22/0x80

## References
- https://git.kernel.org/stable/c/d0553680f94c49bbe0e39eb50d033ba563b4212d
- https://git.kernel.org/stable/c/1740a1e45eee65099a92fb502e1e67e63aad277d
- https://git.kernel.org/stable/c/6950df42a03c9ac9290503ced3f371199cb68fa9
- https://git.kernel.org/stable/c/9ab896775f98ff54b68512f345eed178bf961084
- https://git.kernel.org/stable/c/b6d44072117bba057d50f7a2f96e5d070c65926d
