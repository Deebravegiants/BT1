# [H] cxl/port: Fix use-after-free, permit out-of-order decoder shutdown

## Summary
Severity: High
Advisory: CVE-2024-50226
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-11-09
Source: https://osv.dev/vulnerability/CVE-2024-50226
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.0.0 <6.6.60, >=6.7.0 <6.11.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

cxl/port: Fix use-after-free, permit out-of-order decoder shutdown

In support of investigating an initialization failure report [1],
cxl_test was updated to register mock memory-devices after the mock
root-port/bus device had been registered. That led to cxl_test crashing
with a use-after-free bug with the following signature:

    cxl_port_attach_region: cxl region3: cxl_host_bridge.0:port3 decoder3.0 add: mem0:decoder7.0 @ 0 next: cxl_switch_uport.0 nr_eps: 1 nr_targets: 1
    cxl_port_attach_region: cxl region3: cxl_host_bridge.0:port3 decoder3.0 add: mem4:decoder14.0 @ 1 next: cxl_switch_uport.0 nr_eps: 2 nr_targets: 1
    cxl_port_setup_targets: cxl region3: cxl_switch_uport.0:port6 target[0] = cxl_switch_dport.0 for mem0:decoder7.0 @ 0
1)  cxl_port_setup_targets: cxl region3: cxl_switch_uport.0:port6 target[1] = cxl_switch_dport.4 for mem4:decoder14.0 @ 1
    [..]
    cxld_unregister: cxl decoder14.0:
    cxl_region_decode_reset: cxl_region region3:
    mock_decoder_reset: cxl_port port3: decoder3.0 reset
2)  mock_decoder_reset: cxl_port port3: decoder3.0: out of order reset, expected decoder3.1
    cxl_endpoint_decoder_release: cxl decoder14.0:
    [..]
    cxld_unregister: cxl decoder7.0:
3)  cxl_region_decode_reset: cxl_region region3:
    Oops: general protection fault, probably for non-canonical address 0x6b6b6b6b6b6b6bc3: 0000 [#1] PREEMPT SMP PTI
    [..]
    RIP: 0010:to_cxl_port+0x8/0x60 [cxl_core]
    [..]
    Call Trace:
     <TASK>
     cxl_region_decode_reset+0x69/0x190 [cxl_core]
     cxl_region_detach+0xe8/0x210 [cxl_core]
     cxl_decoder_kill_region+0x27/0x40 [cxl_core]
     cxld_unregister+0x5d/0x60 [cxl_core]

At 1) a region has been established with 2 endpoint decoders (7.0 and
14.0). Those endpoints share a common switch-decoder in the topology
(3.0). At teardown, 2), decoder14.0 is the first to be removed and hits
the "out of order reset case" in the switch decoder. The effect though
is that region3 cleanup is aborted leaving it in-tact and
referencing decoder14.0. At 3) the second attempt to teardown region3
trips over the stale decoder14.0 object which has long since been
deleted.

The fix here is to recognize that the CXL specification places no
mandate on in-order shutdown of switch-decoders, the driver enforces
in-order allocation, and hardware enforces in-order commit. So, rather
than fail and leave objects dangling, always remove them.

In support of making cxl_region_decode_reset() always succeed,
cxl_region_invalidate_memregion() failures are turned into warnings.
Crashing the kernel is ok there since system integrity is at risk if
caches cannot be managed around physical address mutation events like
CXL region destruction.

A new device_for_each_child_reverse_from() is added to cleanup
port->commit_end after all dependent decoders have been disabled. In
other words if decoders are allocated 0->1->2 and disabled 1->2->0 then
port->commit_end only decrements from 2 after 2 has been disabled, and
it decrements all the way to zero since 1 was disabled previously.

## References
- https://git.kernel.org/stable/c/101c268bd2f37e965a5468353e62d154db38838e
- https://git.kernel.org/stable/c/78c8454fdce0eeee962be004eb6d99860c80dad1
- https://git.kernel.org/stable/c/8e1b52c15c81106456437f8e49575040e489e355
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50226.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50226
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
