# [H] can: bcm: track a single source interface for ANYDEV timeout/throttle ops

## Summary
Severity: High
Advisory: CVE-2026-72115
Ecosystem: Linux
CVSS: 8.1 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72115
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.25 <5.10.265, >=5.11.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.148, >=6.7.0 <6.12.101, >=6.13.0 <6.18.42, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

can: bcm: track a single source interface for ANYDEV timeout/throttle ops

An ANYDEV rx op (ifindex == 0) with an active RX timeout and/or
throttle timer has no defined semantics when matching frames arrive
from several interfaces: bcm_rx_handler() can run concurrently for
the same op on different CPUs, racing hrtimer_cancel()/
bcm_rx_starttimer() against bcm_rx_timeout_handler() and causing
spurious RX_TIMEOUT notifications and last_frames corruption. The
same concurrency lets throttled multiplex frames from different
interfaces clobber the single rx_ifindex/rx_stamp fields shared by
the op.

Add op->if_detected to track the first interface that delivers a
matching frame while a timeout/throttle timer is configured, and
reject frames from any other interface for that op. The claim is
decided in bcm_rx_handler() before hrtimer_cancel() touches
op->timer, so a rejected frame can never disturb the claimed
interface's watchdog. RTR-mode ops are excluded via RX_RTR_FRAME,
independent of kt_ival1/kt_ival2, since those may briefly hold a
stale value from an earlier non-RTR configuration.

The claim is released in bcm_notify() on NETDEV_UNREGISTER and in
bcm_rx_setup() when SETTIMER reconfigures the timer values.

A (re-)claim is only possible on CAN devices in NETREG_REGISTERED
dev->reg_state to cover the release in bcm_notify() where reg_state
becomes NETREG_UNREGISTERING until synchronize_net().

## References
- https://git.kernel.org/stable/c/03dfe347c398fa41a7e30e8dc538f12568c183e6
- https://git.kernel.org/stable/c/18b45251e74e35668f0dd0c470549384ae191ecf
- https://git.kernel.org/stable/c/2f5976f54a04e9f18b25283036ac3136be453b17
- https://git.kernel.org/stable/c/3ff8c24b421070a2db99a5cdb86edc9ff339418e
- https://git.kernel.org/stable/c/57cf104da4cf450ae9c16801a3164604b801d2cc
- https://git.kernel.org/stable/c/b6317022b685a430a3ae420456716e3c0c02ef4b
- https://git.kernel.org/stable/c/eca8b44d51fc6ab61022258ec968e55e3073b79e
- https://git.kernel.org/stable/c/f147f48837cb1426521f5b3c3b3134c71128a25d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72115.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72115
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
