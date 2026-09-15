# [H] ice: fix Tx scheduler error handling in XDP callback

## Summary
Severity: High
Advisory: CVE-2025-38127
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-07-03
Source: https://osv.dev/vulnerability/CVE-2025-38127
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.5.0 <6.6.94, >=6.7.0 <6.12.34, >=6.13.0 <6.15.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

ice: fix Tx scheduler error handling in XDP callback

When the XDP program is loaded, the XDP callback adds new Tx queues.
This means that the callback must update the Tx scheduler with the new
queue number. In the event of a Tx scheduler failure, the XDP callback
should also fail and roll back any changes previously made for XDP
preparation.

The previous implementation had a bug that not all changes made by the
XDP callback were rolled back. This caused the crash with the following
call trace:

[  +9.549584] ice 0000:ca:00.0: Failed VSI LAN queue config for XDP, error: -5
[  +0.382335] Oops: general protection fault, probably for non-canonical address 0x50a2250a90495525: 0000 [#1] SMP NOPTI
[  +0.010710] CPU: 103 UID: 0 PID: 0 Comm: swapper/103 Not tainted 6.14.0-net-next-mar-31+ #14 PREEMPT(voluntary)
[  +0.010175] Hardware name: Intel Corporation M50CYP2SBSTD/M50CYP2SBSTD, BIOS SE5C620.86B.01.01.0005.2202160810 02/16/2022
[  +0.010946] RIP: 0010:__ice_update_sample+0x39/0xe0 [ice]

[...]

[  +0.002715] Call Trace:
[  +0.002452]  <IRQ>
[  +0.002021]  ? __die_body.cold+0x19/0x29
[  +0.003922]  ? die_addr+0x3c/0x60
[  +0.003319]  ? exc_general_protection+0x17c/0x400
[  +0.004707]  ? asm_exc_general_protection+0x26/0x30
[  +0.004879]  ? __ice_update_sample+0x39/0xe0 [ice]
[  +0.004835]  ice_napi_poll+0x665/0x680 [ice]
[  +0.004320]  __napi_poll+0x28/0x190
[  +0.003500]  net_rx_action+0x198/0x360
[  +0.003752]  ? update_rq_clock+0x39/0x220
[  +0.004013]  handle_softirqs+0xf1/0x340
[  +0.003840]  ? sched_clock_cpu+0xf/0x1f0
[  +0.003925]  __irq_exit_rcu+0xc2/0xe0
[  +0.003665]  common_interrupt+0x85/0xa0
[  +0.003839]  </IRQ>
[  +0.002098]  <TASK>
[  +0.002106]  asm_common_interrupt+0x26/0x40
[  +0.004184] RIP: 0010:cpuidle_enter_state+0xd3/0x690

Fix this by performing the missing unmapping of XDP queues from
q_vectors and setting the XDP rings pointer back to NULL after all those
queues are released.
Also, add an immediate exit from the XDP callback in case of ring
preparation failure.

## References
- https://git.kernel.org/stable/c/0153f36041b8e52019ebfa8629c13bf8f9b0a951
- https://git.kernel.org/stable/c/0e061abaad1498c5b76c10c594d4359ceb6b9145
- https://git.kernel.org/stable/c/1d3c5d0dec6797eca3a861dab0816fa9505d9c3e
- https://git.kernel.org/stable/c/276849954d7cbe6eec827b21fe2df43f9bf07011
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38127.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38127
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
