# [H] hdlc_ppp: sync per-proto timers before freeing hdlc state

## Summary
Severity: High
Advisory: CVE-2026-63803
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-63803
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <5.10.261, >=5.11.0 <5.15.211, >=5.16.0 <6.1.177, >=6.2.0 <6.6.144, >=6.7.0 <6.12.95, >=6.13.0 <6.18.38, >=6.19.0 <7.1.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

hdlc_ppp: sync per-proto timers before freeing hdlc state

Each PPP control protocol (LCP/IPCP/IPV6CP) embedded in struct ppp
registers a timer via timer_setup(). That struct ppp is the
hdlc->state allocation, which detach_hdlc_protocol() frees with kfree()
in both teardown paths: unregister_hdlc_device() and the re-attach inside
attach_hdlc_protocol().

The ppp proto never registered a .detach callback, so
detach_hdlc_protocol() performs no timer synchronization before the
kfree(). The only cancel, timer_delete(&proto->timer) in ppp_cp_event(),
is partial (it does not wait for a running callback) and only runs on the
->CLOSED transition; ppp_stop()/ppp_close() do not sync either. A
ppp_timer callback already executing (blocked on ppp->lock) survives the
kfree and then dereferences proto->state / ppp->lock in freed memory,
leading to a use-after-free.

Fix this by adding a .detach helper that calls timer_shutdown_sync() on
every per-proto timer. detach_hdlc_protocol() invokes proto->detach(dev)
before kfree(hdlc->state), so timer_shutdown_sync()
now runs on both free paths.
timer_shutdown_sync() is used instead of timer_delete_sync() because the
keepalive path re-arms the timer through add_timer()/mod_timer() and
shutdown blocks any re-activation during teardown.

Initialize the per-protocol timers in ppp_ioctl() when the protocol is
attached, and remove the now-redundant timer_setup() from ppp_start(), so
that the timers are initialized exactly once at attach time and
ppp_timer_release() never operates on uninitialized timer_list
structures. attach_hdlc_protocol() uses kmalloc() (not kzalloc), so
struct ppp's protos[i].timer is uninitialized garbage until the first
timer_setup(); without this init-at-attach, attaching the PPP protocol
without ever bringing the device up would leave timer_shutdown_sync()
operating on uninitialized memory in .detach. Moving the init out of
ppp_start() (which only runs on NETDEV_UP) into the attach path makes the
initialization unconditional and avoids initializing the same timer_list
twice.

This bug was found by static analysis.

## References
- https://git.kernel.org/stable/c/508a0139d3bf60f6a03d2fbfb63a89a9463d983a
- https://git.kernel.org/stable/c/5a84398101bf9f11e84b176343e4e3ba83e668c0
- https://git.kernel.org/stable/c/8308122bc9c065b1f376e081ed300129a2ac9545
- https://git.kernel.org/stable/c/86d80a231bde4cfb64bfbfbfffd83056fc93628f
- https://git.kernel.org/stable/c/a594debfd4e7ec39413647458907f689ef57fd2f
- https://git.kernel.org/stable/c/c64dbef1c0fbd36f9530aa75112acdf6a6d3cfd8
- https://git.kernel.org/stable/c/c78a4e41ab5ead6193ad8a2dd92e8906bae659fa
- https://git.kernel.org/stable/c/ce8f9ddca0c9f217342a8b49efd309aa35b81a36
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63803.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-63803
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
