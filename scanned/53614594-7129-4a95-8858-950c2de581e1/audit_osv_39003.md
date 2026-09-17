# [H] netfilter: flowtable: strictly check for maximum number of actions

## Summary
Severity: High
Advisory: CVE-2026-43329
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-08
Source: https://osv.dev/vulnerability/CVE-2026-43329
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.5.0 <5.15.203, >=5.16.0 <6.1.168, >=6.2.0 <6.6.134, >=6.7.0 <6.12.81, >=6.13.0 <6.18.22, >=6.19.0 <6.19.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: flowtable: strictly check for maximum number of actions

The maximum number of flowtable hardware offload actions in IPv6 is:

* ethernet mangling (4 payload actions, 2 for each ethernet address)
* SNAT (4 payload actions)
* DNAT (4 payload actions)
* Double VLAN (4 vlan actions, 2 for popping vlan, and 2 for pushing)
  for QinQ.
* Redirect (1 action)

Which makes 17, while the maximum is 16. But act_ct supports for tunnels
actions too. Note that payload action operates at 32-bit word level, so
mangling an IPv6 address takes 4 payload actions.

Update flow_action_entry_next() calls to check for the maximum number of
supported actions.

While at it, rise the maximum number of actions per flow from 16 to 24
so this works fine with IPv6 setups.

## References
- https://git.kernel.org/stable/c/504c9456699dcf4d15195ef34a0fa94a80bfc877
- https://git.kernel.org/stable/c/5382bb03e9c33b089d60788478b922a2dca284cc
- https://git.kernel.org/stable/c/57c78bd2e2dd08897acd35b2bf8bcef322e36f5e
- https://git.kernel.org/stable/c/76522fcdbc3a02b568f5d957f7e66fc194abb893
- https://git.kernel.org/stable/c/879959a7a2be814dd57568655eafa3d8f4d0309e
- https://git.kernel.org/stable/c/ead66c77303f760f6c30be96e2e20d5a77cef614
- https://git.kernel.org/stable/c/fe9018d3e94329f1951b00805a8640bc06f56ead
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-43329.json
- https://access.redhat.com/errata/RHSA-2026:23329
- https://access.redhat.com/errata/RHSA-2026:26427
- https://access.redhat.com/errata/RHSA-2026:26428
- https://access.redhat.com/errata/RHSA-2026:27713
- https://access.redhat.com/errata/RHSA-2026:30848
- https://access.redhat.com/errata/RHSA-2026:33215
- https://access.redhat.com/errata/RHSA-2026:33899
- https://access.redhat.com/errata/RHSA-2026:33900
- https://access.redhat.com/errata/RHSA-2026:34094
- https://access.redhat.com/errata/RHSA-2026:34095
- https://access.redhat.com/errata/RHSA-2026:35863
- https://access.redhat.com/errata/RHSA-2026:35896
