# [M] udp: Fix a data-race around sysctl_udp_l3mdev_accept.

## Summary
Severity: Medium
Advisory: CVE-2022-49577
Ecosystem: Linux
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49577
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.11.0 <5.4.208, >=5.5.0 <5.10.134, >=5.11.0 <5.15.58, >=5.16.0 <5.18.15

## Details
In the Linux kernel, the following vulnerability has been resolved:

udp: Fix a data-race around sysctl_udp_l3mdev_accept.

While reading sysctl_udp_l3mdev_accept, it can be changed concurrently.
Thus, we need to add READ_ONCE() to its reader.

## References
- https://git.kernel.org/stable/c/3d72bb4188c708bb16758c60822fc4dda7a95174
- https://git.kernel.org/stable/c/3f2ac2d6511bb0652abf4d7388d65bb9ff1c641c
- https://git.kernel.org/stable/c/cb0d28934ca10f99c47e2c6f451405d6c954fe48
- https://git.kernel.org/stable/c/f39b03bd727a8fea62e82f10fe2e0d753b9930ff
- https://git.kernel.org/stable/c/fcaef69c79ec222e55643e666b80b221e70fa6a8
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49577.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49577
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
