# [H] qede: sync udp_tunnel ports outside qede_lock in the recovery path

## Summary
Severity: High
Advisory: CVE-2026-74523
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74523
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.9.0 <5.10.265, >=5.11.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.151, >=6.7.0 <6.12.103, >=6.13.0 <6.18.44, >=6.19.0 <7.1.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

qede: sync udp_tunnel ports outside qede_lock in the recovery path

A TX timeout on a qede NIC that has VXLAN/GENEVE tunnel ports
configured wedges the rtnetlink control plane of the whole machine:

  NETDEV WATCHDOG: ens6f1 (qede): transmit queue 2 timed out 10226 ms
  [qede_tx_timeout:586(ens6f1)]TX timeout on queue 2!
  [qede_recovery_handler:2665(ens6f0)]Starting a recovery process

The recovery path deadlocks on the driver's own mutex:

  qede_sp_task
   rtnl_lock()
   mutex_lock(&edev->qede_lock)        <- taken
   qede_recovery_handler
    qede_load
    udp_tunnel_nic_reset_ntf
     __udp_tunnel_nic_device_sync
      info->sync_table == qede_udp_tunnel_sync
       mutex_lock(&edev->qede_lock)    <- same task: deadlock

The mutex is not recursive, so the kworker blocks on itself with
rtnl_lock held, and neither lock is ever released. Every task that
calls rtnl_lock() afterwards (ip, ovs-vswitchd, lldpad, IPv6
addrconf, sshd) blocks forever while the node still answers ping.
In a vmcore from an affected production node rtnl_mutex.owner
decodes to the very kworker blocked at the innermost mutex_lock()
above.

Re-sync the tunnel ports from qede_sp_task() after the internal lock
is dropped, still under rtnl_lock as the udp_tunnel API requires.
This mirrors qede_open(), which calls udp_tunnel_nic_reset_ntf()
under rtnl without the internal lock.

qede_recovery_handler() now returns whether it has successfully
reloaded an open device, and the caller re-syncs the ports only in
that case. This keeps the old gating exactly: a device that was down
or a failed recovery returns false, as those paths never reached the
udp_tunnel_nic_reset_ntf() call before either.

This was the only user of the qede_lock()/qede_unlock() helpers, so
remove them.

## References
- https://git.kernel.org/stable/c/19e505ee8bb9e0f0355eda9e9f614fb25fed0070
- https://git.kernel.org/stable/c/451c9075d6c53f2438d110addbeeeea6fac18567
- https://git.kernel.org/stable/c/4626df3f63c9185efba5750fe76ac01ab3351bae
- https://git.kernel.org/stable/c/6f1ef8170d3d8ad9319aa01347945dcdf5cc4f27
- https://git.kernel.org/stable/c/8e1bdf57de91247e57816482966265ada573cc74
- https://git.kernel.org/stable/c/c4c1e5d6bc2b900b2328d6fff93dc8146b858d69
- https://git.kernel.org/stable/c/e382a4efeeae6555b95d9ff336cf3094ee7d336b
- https://git.kernel.org/stable/c/e51becb8f3377a377171ed5bf0082b96e22e6292
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74523.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74523
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
