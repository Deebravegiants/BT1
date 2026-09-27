# [H] net: fix stack overflow when LRO is disabled for virtual interfaces

## Summary
Severity: High
Advisory: CVE-2023-54012
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-24
Source: https://osv.dev/vulnerability/CVE-2023-54012
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.4.0 <5.4.244, >=5.5.0 <5.10.181, >=5.11.0 <5.15.114, >=5.16.0 <6.1.31, >=6.2.0 <6.3.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: fix stack overflow when LRO is disabled for virtual interfaces

When the virtual interface's feature is updated, it synchronizes the
updated feature for its own lower interface.
This propagation logic should be worked as the iteration, not recursively.
But it works recursively due to the netdev notification unexpectedly.
This problem occurs when it disables LRO only for the team and bonding
interface type.

       team0
         |
  +------+------+-----+-----+
  |      |      |     |     |
team1  team2  team3  ...  team200

If team0's LRO feature is updated, it generates the NETDEV_FEAT_CHANGE
event to its own lower interfaces(team1 ~ team200).
It is worked by netdev_sync_lower_features().
So, the NETDEV_FEAT_CHANGE notification logic of each lower interface
work iteratively.
But generated NETDEV_FEAT_CHANGE event is also sent to the upper
interface too.
upper interface(team0) generates the NETDEV_FEAT_CHANGE event for its own
lower interfaces again.
lower and upper interfaces receive this event and generate this
event again and again.
So, the stack overflow occurs.

But it is not the infinite loop issue.
Because the netdev_sync_lower_features() updates features before
generating the NETDEV_FEAT_CHANGE event.
Already synchronized lower interfaces skip notification logic.
So, it is just the problem that iteration logic is changed to the
recursive unexpectedly due to the notification mechanism.

Reproducer:

ip link add team0 type team
ethtool -K team0 lro on
for i in {1..200}
do
        ip link add team$i master team0 type team
        ethtool -K team$i lro on
done

ethtool -K team0 lro off

In order to fix it, the notifier_ctx member of bonding/team is introduced.

## References
- https://git.kernel.org/stable/c/4bb955c4d2830a58c08e2a48ab75d75368e3ff36
- https://git.kernel.org/stable/c/6bf00bb3dc7e5b9fb05488e11616e65d64e975fa
- https://git.kernel.org/stable/c/9ea0c5f90a27b5b884d880e146e0f65f3052e401
- https://git.kernel.org/stable/c/ae9b15fbe63447bc1d3bba3769f409d17ca6fdf6
- https://git.kernel.org/stable/c/cf3b5cd7127cc10c5b12400c545f263f0e5e715c
- https://git.kernel.org/stable/c/ed66e6327a69fec95034cda2ac5b6a57b8b3b622
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/54xxx/CVE-2023-54012.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-54012
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
