# [H] RDMA/hns: Fix NULL pointer derefernce in hns_roce_map_mr_sg()

## Summary
Severity: High
Advisory: CVE-2024-53226
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-12-27
Source: https://osv.dev/vulnerability/CVE-2024-53226
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.10.231, >=5.11.0 <5.15.174, >=5.16.0 <6.1.120, >=6.2.0 <6.6.64, >=6.7.0 <6.11.11, >=6.11.0 <6.12.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

RDMA/hns: Fix NULL pointer derefernce in hns_roce_map_mr_sg()

ib_map_mr_sg() allows ULPs to specify NULL as the sg_offset argument.
The driver needs to check whether it is a NULL pointer before
dereferencing it.

## References
- https://git.kernel.org/stable/c/35f5b68f63aac61d30ce0b0c6beb09b8845a3e65
- https://git.kernel.org/stable/c/52617e76f4963644db71dc0a17e998654dc0c7f4
- https://git.kernel.org/stable/c/6b0d7d6e6883d0ec70cd7b5a02c47c003d5defe7
- https://git.kernel.org/stable/c/6b526d17eed850352d880b93b9bf20b93006bd92
- https://git.kernel.org/stable/c/71becb0e9df78a8d43dfd0efcef18c830a0af477
- https://git.kernel.org/stable/c/8c269bb2cc666ca580271e1a8136c63ac9162e1e
- https://git.kernel.org/stable/c/bd715e191d444992d6ed124f15856da5c1cae2de
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/53xxx/CVE-2024-53226.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-53226
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
