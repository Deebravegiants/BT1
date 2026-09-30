# [M] CVE-2021-47514

## Summary
Severity: Medium
Advisory: CVE-2021-47514
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-24
Source: https://osv.dev/vulnerability/CVE-2021-47514
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

devlink: fix netns refcount leak in devlink_nl_cmd_reload()

While preparing my patch series adding netns refcount tracking,
I spotted bugs in devlink_nl_cmd_reload()

Some error paths forgot to release a refcount on a netns.

To fix this, we can reduce the scope of get_net()/put_net()
section around the call to devlink_reload().

## References
- https://git.kernel.org/stable/c/4b7e90672af8e0c78205db006f1b0a20ebd07f5f
- https://git.kernel.org/stable/c/4dbb0dad8e63fcd0b5a117c2861d2abe7ff5f186
- https://git.kernel.org/stable/c/fe30b70ca84da9c4aca85c03ad86e7a9b89c5ded
