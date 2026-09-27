# [H] RDMA/mlx5: Add check for srq max_sge attribute

## Summary
Severity: High
Advisory: CVE-2024-40990
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-07-12
Source: https://osv.dev/vulnerability/CVE-2024-40990
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.11.0 <5.10.221, >=5.11.0 <5.15.162, >=5.16.0 <6.1.96, >=6.2.0 <6.6.36, >=6.7.0 <6.9.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

RDMA/mlx5: Add check for srq max_sge attribute

max_sge attribute is passed by the user, and is inserted and used
unchecked, so verify that the value doesn't exceed maximum allowed value
before using it.

## References
- https://git.kernel.org/stable/c/1e692244bf7dd827dd72edc6c4a3b36ae572f03c
- https://git.kernel.org/stable/c/36ab7ada64caf08f10ee5a114d39964d1f91e81d
- https://git.kernel.org/stable/c/4ab99e3613139f026d2d8ba954819e2876120ab3
- https://git.kernel.org/stable/c/7186b81c1f15e39069b1af172c6a951728ed3511
- https://git.kernel.org/stable/c/999586418600b4b3b93c2a0edd3a4ca71ee759bf
- https://git.kernel.org/stable/c/e0deb0e9c967b61420235f7f17a4450b4b4d6ce2
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/40xxx/CVE-2024-40990.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-40990
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
