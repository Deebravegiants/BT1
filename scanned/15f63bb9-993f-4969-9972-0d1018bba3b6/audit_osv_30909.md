# [H] net: mscc: ocelot: fix incorrect IFH SRC_PORT field in ocelot_ifh_set_basic()

## Summary
Severity: High
Advisory: CVE-2024-56717
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-12-29
Source: https://osv.dev/vulnerability/CVE-2024-56717
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.1.122, >=6.2.0 <6.6.68, >=6.7.0 <6.12.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: mscc: ocelot: fix incorrect IFH SRC_PORT field in ocelot_ifh_set_basic()

Packets injected by the CPU should have a SRC_PORT field equal to the
CPU port module index in the Analyzer block (ocelot->num_phys_ports).

The blamed commit copied the ocelot_ifh_set_basic() call incorrectly
from ocelot_xmit_common() in net/dsa/tag_ocelot.c. Instead of calling
with "x", it calls with BIT_ULL(x), but the field is not a port mask,
but rather a single port index.

[ side note: this is the technical debt of code duplication :( ]

The error used to be silent and doesn't appear to have other
user-visible manifestations, but with new changes in the packing
library, it now fails loudly as follows:

------------[ cut here ]------------
Cannot store 0x40 inside bits 46-43 - will truncate
sja1105 spi2.0: xmit timed out
WARNING: CPU: 1 PID: 102 at lib/packing.c:98 __pack+0x90/0x198
sja1105 spi2.0: timed out polling for tstamp
CPU: 1 UID: 0 PID: 102 Comm: felix_xmit
Tainted: G        W        N 6.13.0-rc1-00372-gf706b85d972d-dirty #2605
Call trace:
 __pack+0x90/0x198 (P)
 __pack+0x90/0x198 (L)
 packing+0x78/0x98
 ocelot_ifh_set_basic+0x260/0x368
 ocelot_port_inject_frame+0xa8/0x250
 felix_port_deferred_xmit+0x14c/0x258
 kthread_worker_fn+0x134/0x350
 kthread+0x114/0x138

The code path pertains to the ocelot switchdev driver and to the felix
secondary DSA tag protocol, ocelot-8021q. Here seen with ocelot-8021q.

The messenger (packing) is not really to blame, so fix the original
commit instead.

## References
- https://git.kernel.org/stable/c/2d5df3a680ffdaf606baa10636bdb1daf757832e
- https://git.kernel.org/stable/c/2f3c62ffe88116cd2a39cd73e01103535599970f
- https://git.kernel.org/stable/c/59c4ca8d8d7918eb6e2df91d2c254827264be309
- https://git.kernel.org/stable/c/a8836eae3288c351acd3b2743d2fad2a4ee2bd56
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56717.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-56717
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
