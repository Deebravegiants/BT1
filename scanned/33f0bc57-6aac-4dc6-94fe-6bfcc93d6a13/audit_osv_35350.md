# [H] erspan: Initialize options_len before referencing options.

## Summary
Severity: High
Advisory: CVE-2025-71128
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-01-14
Source: https://osv.dev/vulnerability/CVE-2025-71128
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.15.0 <6.18.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

erspan: Initialize options_len before referencing options.

The struct ip_tunnel_info has a flexible array member named
options that is protected by a counted_by(options_len)
attribute.

The compiler will use this information to enforce runtime bounds
checking deployed by FORTIFY_SOURCE string helpers.

As laid out in the GCC documentation, the counter must be
initialized before the first reference to the flexible array
member.

After scanning through the files that use struct ip_tunnel_info
and also refer to options or options_len, it appears the normal
case is to use the ip_tunnel_info_opts_set() helper.

Said helper would initialize options_len properly before copying
data into options, however in the GRE ERSPAN code a partial
update is done, preventing the use of the helper function.

Before this change the handling of ERSPAN traffic in GRE tunnels
would cause a kernel panic when the kernel is compiled with
GCC 15+ and having FORTIFY_SOURCE configured:

memcpy: detected buffer overflow: 4 byte write of buffer size 0

Call Trace:
 <IRQ>
 __fortify_panic+0xd/0xf
 erspan_rcv.cold+0x68/0x83
 ? ip_route_input_slow+0x816/0x9d0
 gre_rcv+0x1b2/0x1c0
 gre_rcv+0x8e/0x100
 ? raw_v4_input+0x2a0/0x2b0
 ip_protocol_deliver_rcu+0x1ea/0x210
 ip_local_deliver_finish+0x86/0x110
 ip_local_deliver+0x65/0x110
 ? ip_rcv_finish_core+0xd6/0x360
 ip_rcv+0x186/0x1a0

Reported-at: https://launchpad.net/bugs/2129580

## References
- https://git.kernel.org/stable/c/35ddf66c65eff93fff91406756ba273600bf61a3
- https://git.kernel.org/stable/c/b282b2a9eed848587c1348abdd5d83fa346a2743
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/71xxx/CVE-2025-71128.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-71128
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
