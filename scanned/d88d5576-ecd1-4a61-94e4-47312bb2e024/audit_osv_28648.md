# [H] net/mlx5e: fix a double-free in arfs_create_groups

## Summary
Severity: High
Advisory: CVE-2024-35835
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-17
Source: https://osv.dev/vulnerability/CVE-2024-35835
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.7.0 <4.19.307, >=4.20.0 <5.4.269, >=5.5.0 <5.10.210, >=5.11.0 <5.15.149, >=5.16.0 <6.1.76, >=6.2.0 <6.6.15, >=6.7.0 <6.7.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/mlx5e: fix a double-free in arfs_create_groups

When `in` allocated by kvzalloc fails, arfs_create_groups will free
ft->g and return an error. However, arfs_create_table, the only caller of
arfs_create_groups, will hold this error and call to
mlx5e_destroy_flow_table, in which the ft->g will be freed again.

## References
- https://git.kernel.org/stable/c/2501afe6c4c9829d03abe9a368b83d9ea1b611b7
- https://git.kernel.org/stable/c/3c6d5189246f590e4e1f167991558bdb72a4738b
- https://git.kernel.org/stable/c/42876db001bbea7558e8676d1019f08f9390addb
- https://git.kernel.org/stable/c/66cc521a739ccd5da057a1cb3d6346c6d0e7619b
- https://git.kernel.org/stable/c/b21db3f1ab7967a81d6bbd328d28fe5a4c07a8a7
- https://git.kernel.org/stable/c/c57ca114eb00e03274dd38108d07a3750fa3c056
- https://git.kernel.org/stable/c/cf116d9c3c2aebd653c2dfab5b10c278e9ec3ee5
- https://git.kernel.org/stable/c/e3d3ed8c152971dbe64c92c9ecb98fdb52abb629
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://lists.debian.org/debian-lts-announce/2024/06/msg00020.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/35xxx/CVE-2024-35835.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-35835
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
