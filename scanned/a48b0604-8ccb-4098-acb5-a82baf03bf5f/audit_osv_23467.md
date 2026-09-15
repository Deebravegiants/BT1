# [H] net/mlx5e: IPoIB, Block PKEY interfaces with less rx queues than parent

## Summary
Severity: High
Advisory: CVE-2022-48883
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-08-21
Source: https://osv.dev/vulnerability/CVE-2022-48883
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.17.0 <6.1.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/mlx5e: IPoIB, Block PKEY interfaces with less rx queues than parent

A user is able to configure an arbitrary number of rx queues when
creating an interface via netlink. This doesn't work for child PKEY
interfaces because the child interface uses the parent receive channels.

Although the child shares the parent's receive channels, the number of
rx queues is important for the channel_stats array: the parent's rx
channel index is used to access the child's channel_stats. So the array
has to be at least as large as the parent's rx queue size for the
counting to work correctly and to prevent out of bound accesses.

This patch checks for the mentioned scenario and returns an error when
trying to create the interface. The error is propagated to the user.

## References
- https://git.kernel.org/stable/c/31c70bfe58ef09fe36327ddcced9143a16e9e83d
- https://git.kernel.org/stable/c/5844a46f09f768da866d6b0ffbf1a9073266bf24
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/48xxx/CVE-2022-48883.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-48883
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
