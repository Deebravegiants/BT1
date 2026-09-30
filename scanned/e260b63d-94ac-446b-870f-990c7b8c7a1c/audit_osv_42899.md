# [H] can: bcm: add locking when updating filter and timer values

## Summary
Severity: High
Advisory: CVE-2026-72121
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72121
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.10.265, >=5.11.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.148, >=6.7.0 <6.12.101, >=6.13.0 <6.18.42, >=6.15.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

can: bcm: add locking when updating filter and timer values

KCSAN detected a simultaneous access to timer values that can be
overwritten in bcm_rx_setup() when updating timer and filter content
while bcm_rx_handler(), bcm_rx_timeout_handler() or bcm_rx_thr_handler()
run concurrently on incoming CAN traffic.

Protect the timer (ival1/ival2/kt_ival1/kt_ival2/kt_lastmsg) and filter
(nframes/flags/frames/last_frames) updates in bcm_rx_setup() with a new
per-op bcm_rx_update_lock, taken with the matching scope in the RX
handlers. memcpy_from_msg() is staged into a temporary buffer before the
lock is taken, since it can sleep and must not run under a spinlock.

hrtimer_cancel() is always called without bcm_rx_update_lock held, since
bcm_rx_timeout_handler()/bcm_rx_thr_handler() take the same lock and a
running callback would otherwise deadlock against the canceller.

Also close a related race: bcm_rx_setup() cleared the RTR flag in the
stored reply frame's can_id as a separate, unprotected step after the
frame content was already installed, so a concurrent bcm_rx_handler()
could transmit a stale reply with CAN_RTR_FLAG still set. Fold that
normalization into the initial frame preparation instead (on the staged
buffer for updates, directly on op->frames pre-registration for new
ops), so the installed frame is always atomically self-consistent.

bcm_rx_handler()'s RX_RTR_FRAME check now takes a lock-protected
snapshot of op->flags before deciding whether to call bcm_can_tx(),
but does not hold the lock across that call.

Also take a lock-protected snapshot of the currframe in bcm_can_tx()
to avoid partly overwrites by content updates in bcm_tx_setup().
Finally check if a TX_RESET_MULTI_IDX/SETTIMER might have reset
op->currframe between the two locked sections in bcm_can_tx().

Omit calling hrtimer_forward() with zero interval in bcm_rx_thr_handler().
kt_ival2 may have been concurrently cleared by bcm_rx_setup() before it
cancels this timer, so check kt_ival2 inside the bcm_rx_update_lock.

## References
- https://git.kernel.org/stable/c/19b1994069dd29478ba767de1f98f14a088198dc
- https://git.kernel.org/stable/c/749179c2e25b95d22499ed29096b3e02d6dfd2b4
- https://git.kernel.org/stable/c/834cbca3b12e46887f7a9b35f1981a888360ea4c
- https://git.kernel.org/stable/c/96994180bd7b248b0cc698afe926e23fc1bda59b
- https://git.kernel.org/stable/c/a7c369e7da8203e2b5be12bbcac7b9ab2ed5b658
- https://git.kernel.org/stable/c/a7eb6db1cd3f7b556a301dc1265945ad112089f7
- https://git.kernel.org/stable/c/caa8704a7f3cb7806331596195385437126ecb3a
- https://git.kernel.org/stable/c/fc9f5ee1b073bd233d9c604e338af4ebb42cbc33
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72121.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72121
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
