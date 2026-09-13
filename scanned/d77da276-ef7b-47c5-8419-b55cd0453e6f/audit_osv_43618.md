# [C] net: bridge: stop fast-leave after deleting a port group

## Summary
Severity: Critical
Advisory: CVE-2026-74480
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74480
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.11.0 <5.10.265, >=5.11.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.151, >=6.7.0 <6.12.103, >=6.13.0 <6.18.44, >=6.19.0 <7.1.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: bridge: stop fast-leave after deleting a port group

br_multicast_leave_group() iterates mp->ports with pp = &p->next in
its fast-leave path. After br_multicast_del_pg() removes p,
continuing the loop advances pp through the deleted entry.

If multicast-to-unicast was enabled, the bridge can hold multiple port
groups for the same port and group with different source MAC
addresses. Once multicast-to-unicast is disabled,
br_port_group_equal() matches those entries by port only. A fast leave
can then delete one entry and continue from its stale next pointer,
leaving mp->ports pointing at a deleted port group.

Fast leave only needs to remove one matching port group. Break after
br_multicast_del_pg() so the loop stops before dereferencing the
removed entry.

## References
- https://git.kernel.org/stable/c/0309ebbc570000ea0df11c06b69798e5860c5f6f
- https://git.kernel.org/stable/c/159ad90cb929c033308bb39a2c5f8fbf393b77aa
- https://git.kernel.org/stable/c/1a109cc9890d017c41d77e6c82da739579c49f0b
- https://git.kernel.org/stable/c/4695430e8132420bf8de94da3eb36a6cf35fde6b
- https://git.kernel.org/stable/c/482bcb85139addb4e8ac8ed10baeda3e0aad4031
- https://git.kernel.org/stable/c/4c57056ca6aace2e9f94ae9298bf49ef6b0c95e4
- https://git.kernel.org/stable/c/a39789f211b8a4125f0c70e05b30cf715f4f187d
- https://git.kernel.org/stable/c/d6c32e2e25a9a06ba021030e26b6d602a277eb72
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74480.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74480
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
