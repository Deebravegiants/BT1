# [H] team: fix header_ops type confusion with non-Ethernet ports

## Summary
Severity: High
Advisory: CVE-2026-31502
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-22
Source: https://osv.dev/vulnerability/CVE-2026-31502
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.7.0 <6.6.145, >=6.7.0 <6.12.80, >=6.13.0 <6.18.21, >=6.19.0 <6.19.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

team: fix header_ops type confusion with non-Ethernet ports

Similar to commit 950803f72547 ("bonding: fix type confusion in
bond_setup_by_slave()") team has the same class of header_ops type
confusion.

For non-Ethernet ports, team_setup_by_port() copies port_dev->header_ops
directly. When the team device later calls dev_hard_header() or
dev_parse_header(), these callbacks can run with the team net_device
instead of the real lower device, so netdev_priv(dev) is interpreted as
the wrong private type and can crash.

The syzbot report shows a crash in bond_header_create(), but the root
cause is in team: the topology is gre -> bond -> team, and team calls
the inherited header_ops with its own net_device instead of the lower
device, so bond_header_create() receives a team device and interprets
netdev_priv() as bonding private data, causing a type confusion crash.

Fix this by introducing team header_ops wrappers for create/parse,
selecting a team port under RCU, and calling the lower device callbacks
with port->dev, so each callback always sees the correct net_device
context.

Also pass the selected lower device to the lower parse callback, so
recursion is bounded in stacked non-Ethernet topologies and parse
callbacks always run with the correct device context.

## References
- https://git.kernel.org/stable/c/0a7468ed49a6b65d34abcc6eb60e15f7f6d34da0
- https://git.kernel.org/stable/c/20491d384d973a63fbdaf7a71e38d69b0659ea55
- https://git.kernel.org/stable/c/420e5aad7ba89e8f79e2dc8327b0c0c24c1c1d53
- https://git.kernel.org/stable/c/425000dbf17373a4ab8be9428f5dc055ef870a56
- https://git.kernel.org/stable/c/6d3161fa3eee64d46b766fb0db33ec7f300ef52d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31502.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31502
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
