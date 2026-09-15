# [M] CVE-2022-39190

## Summary
Severity: Medium
Advisory: CVE-2022-39190
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-09-02
Source: https://osv.dev/vulnerability/CVE-2022-39190
Type: osv

## Details
An issue was discovered in net/netfilter/nf_tables_api.c in the Linux kernel before 5.19.6. A denial of service can occur upon binding to an already bound chain.

## References
- https://lore.kernel.org/all/20220824220330.64283-12-pablo%40netfilter.org/
- https://lists.debian.org/debian-lts-announce/2022/11/msg00001.html
- https://twitter.com/pr0Ln
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.19.6
- https://github.com/torvalds/linux/commit/e02f0d3970404bfea385b6edb86f2d936db0ea2b
