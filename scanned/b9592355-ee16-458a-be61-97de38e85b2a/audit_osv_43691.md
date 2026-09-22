# [C] sctp: clear new_transport when removing a peer

## Summary
Severity: Critical
Advisory: CVE-2026-74586
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-22
Source: https://osv.dev/vulnerability/CVE-2026-74586
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.2.0 <5.10.265, >=5.11.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.152, >=6.7.0 <6.12.104, >=6.13.0 <6.18.45, >=6.19.0 <7.1.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

sctp: clear new_transport when removing a peer

sctp_process_asconf_param() stores a newly added peer transport in
asoc->new_transport. After all parameters in the ASCONF chunk have been
processed, sctp_sf_do_asconf() uses this pointer to send a HEARTBEAT to the
new transport.

An authenticated ASCONF from a remote SCTP peer can add a transport and
remove it again with a wildcard DEL-IP parameter in the same chunk. The
wildcard deletion preserves the transport on which the ASCONF arrived, but
removes the newly added transport through
sctp_assoc_del_nonprimary_peers(). The removal does not clear
asoc->new_transport, leaving it pointing to the removed transport.

sctp_sf_do_asconf() then creates a HEARTBEAT whose chunk->transport points
to the removed transport without holding a transport reference. During
local address replacement, src_out_of_asoc_ok keeps this HEARTBEAT on
control_chunk_list. After the transport is freed by RCU, a successful
ASCONF_ACK for the replacement address releases the queued HEARTBEAT and
sctp_outq_select_transport() reads the freed transport's state.

The issue was found during a static audit of SCTP objects. With an
authenticated peer, the reproducer triggered the same KASAN report in 2
of 2 unpatched runs on a KASAN-enabled netdev/main kernel:

  BUG: KASAN: slab-use-after-free in sctp_outq_select_transport
  Read of size 4 at addr ffff88800b9bd95c by task python3/197

  Call Trace:
   sctp_outq_select_transport+0x549/0x8b0 [sctp]
   sctp_outq_flush+0x306/0x2c60 [sctp]
   sctp_transport_immediate_rtx+0xaf/0x260 [sctp]
   sctp_process_asconf_ack+0xa48/0xf70 [sctp]

  Allocated by task 197:
   sctp_transport_new+0x68/0x650 [sctp]
   sctp_assoc_add_peer+0x258/0x12a0 [sctp]
   sctp_process_asconf+0x5e9/0x1090 [sctp]

  Last potentially related work creation:
   __call_rcu_common.constprop.0+0x77/0xb70
   sctp_assoc_del_nonprimary_peers+0x7c/0xd0 [sctp]
   sctp_process_asconf+0xd9c/0x1090 [sctp]

The first invalid access was a four-byte read of transport->state at
net/sctp/outqueue.c:833. The same reproducer completed the full
authenticated ASCONF and local-address replacement sequence with this
change without a KASAN report or oops.

Clear new_transport when its peer is removed, before it can be used to
create the HEARTBEAT.

## References
- https://git.kernel.org/stable/c/163847552a571bd55094291f4ffcdc1de0f14a7b
- https://git.kernel.org/stable/c/291accf36febce751021888de5f15090f4875b56
- https://git.kernel.org/stable/c/31efa656cf6aface26e88f038c14f22ee6ca1500
- https://git.kernel.org/stable/c/3b539b317cd052236fed0350364ff1268996ba46
- https://git.kernel.org/stable/c/beb33f8ee1ca83acddb2a5ae80f3d22ec550b4c3
- https://git.kernel.org/stable/c/c0f973bb5118dd1b146cda3fcc8af6f6057befec
- https://git.kernel.org/stable/c/ca33df36aa0143a1d04f57d2086020c12e7eddb7
- https://git.kernel.org/stable/c/db9d8e3b670f841755bc2018f178472dc6064d27
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74586.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74586
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
