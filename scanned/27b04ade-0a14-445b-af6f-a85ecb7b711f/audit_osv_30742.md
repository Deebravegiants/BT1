# [M] Drivers: hv: util: Avoid accessing a ringbuffer not initialized yet

## Summary
Severity: Medium
Advisory: CVE-2024-55916
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-01-11
Source: https://osv.dev/vulnerability/CVE-2024-55916
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.9.0 <5.4.289, >=5.5.0 <5.10.233, >=5.11.0 <5.15.176, >=5.16.0 <6.1.122, >=6.2.0 <6.6.68, >=6.7.0 <6.12.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

Drivers: hv: util: Avoid accessing a ringbuffer not initialized yet

If the KVP (or VSS) daemon starts before the VMBus channel's ringbuffer is
fully initialized, we can hit the panic below:

hv_utils: Registering HyperV Utility Driver
hv_vmbus: registering driver hv_utils
...
BUG: kernel NULL pointer dereference, address: 0000000000000000
CPU: 44 UID: 0 PID: 2552 Comm: hv_kvp_daemon Tainted: G E 6.11.0-rc3+ #1
RIP: 0010:hv_pkt_iter_first+0x12/0xd0
Call Trace:
...
 vmbus_recvpacket
 hv_kvp_onchannelcallback
 vmbus_on_event
 tasklet_action_common
 tasklet_action
 handle_softirqs
 irq_exit_rcu
 sysvec_hyperv_stimer0
 </IRQ>
 <TASK>
 asm_sysvec_hyperv_stimer0
...
 kvp_register_done
 hvt_op_read
 vfs_read
 ksys_read
 __x64_sys_read

This can happen because the KVP/VSS channel callback can be invoked
even before the channel is fully opened:
1) as soon as hv_kvp_init() -> hvutil_transport_init() creates
/dev/vmbus/hv_kvp, the kvp daemon can open the device file immediately and
register itself to the driver by writing a message KVP_OP_REGISTER1 to the
file (which is handled by kvp_on_msg() ->kvp_handle_handshake()) and
reading the file for the driver's response, which is handled by
hvt_op_read(), which calls hvt->on_read(), i.e. kvp_register_done().

2) the problem with kvp_register_done() is that it can cause the
channel callback to be called even before the channel is fully opened,
and when the channel callback is starting to run, util_probe()->
vmbus_open() may have not initialized the ringbuffer yet, so the
callback can hit the panic of NULL pointer dereference.

To reproduce the panic consistently, we can add a "ssleep(10)" for KVP in
__vmbus_open(), just before the first hv_ringbuffer_init(), and then we
unload and reload the driver hv_utils, and run the daemon manually within
the 10 seconds.

Fix the panic by reordering the steps in util_probe() so the char dev
entry used by the KVP or VSS daemon is not created until after
vmbus_open() has completed. This reordering prevents the race condition
from happening.

## References
- https://git.kernel.org/stable/c/042253c57be901bfd19f15b68267442b70f510d5
- https://git.kernel.org/stable/c/07a756a49f4b4290b49ea46e089cbe6f79ff8d26
- https://git.kernel.org/stable/c/3dd7a30c6d7f90afcf19e9b072f572ba524d7ec6
- https://git.kernel.org/stable/c/718fe694a334be9d1a89eed22602369ac18d6583
- https://git.kernel.org/stable/c/89fcec5e466b3ac9b376e0d621c71effa1a7983f
- https://git.kernel.org/stable/c/d81f4e73aff9b861671df60e5100ad25cc16fbf8
- https://git.kernel.org/stable/c/f091a224a2c82f1e302b1768d73bb6332f687321
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/55xxx/CVE-2024-55916.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-55916
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
