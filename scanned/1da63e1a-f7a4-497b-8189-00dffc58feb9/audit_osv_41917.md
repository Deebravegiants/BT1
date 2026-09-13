# [H] batman-adv: tp_meter: directly shut down timer on cleanup

## Summary
Severity: High
Advisory: CVE-2026-64093
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-64093
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.8.0 <5.15.210, >=5.16.0 <6.1.176, >=6.2.0 <6.6.143, >=6.7.0 <6.12.93, >=6.13.0 <6.18.34, >=6.19.0 <7.0.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

batman-adv: tp_meter: directly shut down timer on cleanup

batadv_tp_sender_cleanup() was calling timer_delete_sync() followed by
timer_delete() to guard against the timer handler re-arming itself between
the two calls. This double-deletion hack relied on the sending status being
set to 0 to suppress re-arming.

Replace both calls with a single timer_shutdown_sync(). This function both
waits for any running timer callback to complete (like timer_delete_sync())
and permanently disarms the timer so it cannot be re-armed afterwards,
making re-arming prevention unconditional and self-documenting.

The re-arming property is also required because otherwise:

1. context 0 (batadv_tp_recv_ack()) checks in
   batadv_tp_reset_sender_timer() if sending is still 1 -> it is
2. context 1 changes in batadv_tp_sender_shutdown() sending to 0 and in
   this process forces the kthread to stop timer in
   batadv_tp_sender_cleanup()
3. context 0 continues in batadv_tp_reset_sender_timer() and rearms the
   timer -> but the reference for it is already gone

## References
- https://git.kernel.org/stable/c/00bf4bb9947b1190a8be8d9b6a1bcbfa3707785c
- https://git.kernel.org/stable/c/5bc2d50fb66b46f86543d5153a188eb1486d0b6e
- https://git.kernel.org/stable/c/74a76634055462833446684fd526d73c290ea43a
- https://git.kernel.org/stable/c/770bf0a35f0620b526fd4193889d1e77084e4c43
- https://git.kernel.org/stable/c/933880a8bc9b4042223a79255c0b1021cdc36991
- https://git.kernel.org/stable/c/d5487249a81ea658717614009c8f46acc5b7101a
- https://git.kernel.org/stable/c/f86b20ec8d17d77bddc02c5c86cfa2389d84ecff
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64093.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64093
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
