# [C] RDMA/erdma: Prevent use-after-free in erdma_accept_newconn()

## Summary
Severity: Critical
Advisory: CVE-2025-22088
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-04-16
Source: https://osv.dev/vulnerability/CVE-2025-22088
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.0.0 <6.1.134, >=6.2.0 <6.6.87, >=6.7.0 <6.12.23, >=6.13.0 <6.13.11, >=6.14.0 <6.14.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

RDMA/erdma: Prevent use-after-free in erdma_accept_newconn()

After the erdma_cep_put(new_cep) being called, new_cep will be freed,
and the following dereference will cause a UAF problem. Fix this issue.

## References
- https://git.kernel.org/stable/c/667a628ab67d359166799fad89b3c6909599558a
- https://git.kernel.org/stable/c/78411a133312ce7d8a3239c76a8fd85bca1cc10f
- https://git.kernel.org/stable/c/7aa6bb5276d9fec98deb05615a086eeb893854ad
- https://git.kernel.org/stable/c/83437689249e6a17b25e27712fbee292e42e7855
- https://git.kernel.org/stable/c/a114d25d584c14019d31dbf2163780c47415a187
- https://git.kernel.org/stable/c/bc1db4d8f1b0dc480d7d745a60a8cc94ce2badd4
- https://lists.debian.org/debian-lts-announce/2025/05/msg00045.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/22xxx/CVE-2025-22088.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-22088
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
