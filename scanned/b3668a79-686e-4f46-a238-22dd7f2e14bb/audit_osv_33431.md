# [H] net: enetc: fix the deadlock of enetc_mdio_lock

## Summary
Severity: High
Advisory: CVE-2025-40347
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-12-16
Source: https://osv.dev/vulnerability/CVE-2025-40347
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.12.0 <6.1.175, >=6.2.0 <6.6.115, >=6.7.0 <6.12.56, >=6.13.0 <6.17.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: enetc: fix the deadlock of enetc_mdio_lock

After applying the workaround for err050089, the LS1028A platform
experiences RCU stalls on RT kernel. This issue is caused by the
recursive acquisition of the read lock enetc_mdio_lock. Here list some
of the call stacks identified under the enetc_poll path that may lead to
a deadlock:

enetc_poll
  -> enetc_lock_mdio
  -> enetc_clean_rx_ring OR napi_complete_done
     -> napi_gro_receive
        -> enetc_start_xmit
           -> enetc_lock_mdio
           -> enetc_map_tx_buffs
           -> enetc_unlock_mdio
  -> enetc_unlock_mdio

After enetc_poll acquires the read lock, a higher-priority writer attempts
to acquire the lock, causing preemption. The writer detects that a
read lock is already held and is scheduled out. However, readers under
enetc_poll cannot acquire the read lock again because a writer is already
waiting, leading to a thread hang.

Currently, the deadlock is avoided by adjusting enetc_lock_mdio to prevent
recursive lock acquisition.

## References
- https://git.kernel.org/stable/c/1f92f5bd057a4fad9dab6af17963cdd21e5da6ed
- https://git.kernel.org/stable/c/2781ca82ce8cad263d80b617addb727e6a84c9e5
- https://git.kernel.org/stable/c/2e55a49dc3b2a6b23329e4fbbd8a5feb20e220aa
- https://git.kernel.org/stable/c/50bd33f6b3922a6b760aa30d409cae891cec8fb5
- https://git.kernel.org/stable/c/a649161526736f48bcc592e3a412e5bcd7dd9e24
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40347.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-40347
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
