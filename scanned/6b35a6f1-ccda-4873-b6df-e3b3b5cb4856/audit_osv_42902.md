# [H] can: isotp: serialize TX state transitions under so->rx_lock

## Summary
Severity: High
Advisory: CVE-2026-72124
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72124
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.10.0 <5.10.265, >=5.11.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.148, >=6.7.0 <6.12.101, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

can: isotp: serialize TX state transitions under so->rx_lock

The TX state machine (so->tx.state) is driven from three contexts:
sendmsg() claiming and progressing a transfer, the RX path consuming
Flow Control/echo frames, and two hrtimers timing out a stalled
transfer. Mixing a lock-free cmpxchg() claim in sendmsg() with
hrtimer_cancel() calls made under so->rx_lock elsewhere left windows
where a frame or timer callback could act on a state that had already
moved on, corrupting an unrelated transfer.

so->rx_lock now covers the full lifecycle of a TX claim: sendmsg()
takes it to check so->tx.state is ISOTP_IDLE, switch it to
ISOTP_SENDING, bump so->tx_gen and drain the previous transfer's
timers - all as one critical section. isotp_rcv_fc()/isotp_rcv_cf()
already run under this lock via isotp_rcv(), and isotp_rcv_echo() now
takes it itself, so none of them can ever observe a transfer mid-claim.
This also means a transfer can no longer be handed to sendmsg()'s
cleanup paths (signal or send error) while another thread is
concurrently claiming or finishing it, so those paths can cancel
timers and reset the state unconditionally.

isotp_release() claims the socket the same way, so a racing sendmsg()
sees a consistent ISOTP_SHUTDOWN and skips arming its timer or sending.

Only the hrtimer callbacks stay outside so->rx_lock, since they run
under so->rx_lock's cancellation elsewhere and taking it themselves
would deadlock. so->tx_gen lets them recognize whether the transfer
they timed out is still the one currently active, so they don't
report an error against a transfer that has since completed or been
superseded.

## References
- https://git.kernel.org/stable/c/0b05eca9589f609e2491b528dccf683168a4cda8
- https://git.kernel.org/stable/c/377a8f500704da42ed86a4541ed930e9dcfdb2ea
- https://git.kernel.org/stable/c/37beb16e08cae94cc05840c7274225e3b0b38ae7
- https://git.kernel.org/stable/c/4f1fdf1a1c317bcac0c6b6c8e12642c9983de1ca
- https://git.kernel.org/stable/c/6da8119e8dd542194103139812d1a4b7dcd1aedd
- https://git.kernel.org/stable/c/a7d90e7b5e75d7406c889fe36e9a61ee364a00cb
- https://git.kernel.org/stable/c/bbedeb67a9a684f2fb78c55bd3662c400526715e
- https://git.kernel.org/stable/c/cf070fe33bfbd1a4c21236078fadb35dd223a157
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72124.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72124
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
