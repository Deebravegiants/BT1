# [H] bridge: cfm: Fix race condition in peer_mep deletion

## Summary
Severity: High
Advisory: CVE-2026-23393
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-03-25
Source: https://osv.dev/vulnerability/CVE-2026-23393
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.11.0 <6.12.78, >=6.13.0 <6.18.20, >=6.19.0 <6.19.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

bridge: cfm: Fix race condition in peer_mep deletion

When a peer MEP is being deleted, cancel_delayed_work_sync() is called
on ccm_rx_dwork before freeing. However, br_cfm_frame_rx() runs in
softirq context under rcu_read_lock (without RTNL) and can re-schedule
ccm_rx_dwork via ccm_rx_timer_start() between cancel_delayed_work_sync()
returning and kfree_rcu() being called.

The following is a simple race scenario:

           cpu0                                     cpu1

mep_delete_implementation()
  cancel_delayed_work_sync(ccm_rx_dwork);
                                           br_cfm_frame_rx()
                                             // peer_mep still in hlist
                                             if (peer_mep->ccm_defect)
                                               ccm_rx_timer_start()
                                                 queue_delayed_work(ccm_rx_dwork)
  hlist_del_rcu(&peer_mep->head);
  kfree_rcu(peer_mep, rcu);
                                           ccm_rx_work_expired()
                                             // on freed peer_mep

To prevent this, cancel_delayed_work_sync() is replaced with
disable_delayed_work_sync() in both peer MEP deletion paths, so
that subsequent queue_delayed_work() calls from br_cfm_frame_rx()
are silently rejected.

The cc_peer_disable() helper retains cancel_delayed_work_sync()
because it is also used for the CC enable/disable toggle path where
the work must remain re-schedulable.

## References
- https://git.kernel.org/stable/c/1fd81151f65927fd9edb8ecd12ad45527dbbe5ab
- https://git.kernel.org/stable/c/3715a00855316066cdda69d43648336367422127
- https://git.kernel.org/stable/c/d8f35767bacb3c7769d470a41cf161e3f3c07e70
- https://git.kernel.org/stable/c/e89dbd2736a45f0507949af4748cbbf3ff793146
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23393.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-23393
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
