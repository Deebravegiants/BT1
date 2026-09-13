# [C] svcrdma: bound check rq_pages index in inline path

## Summary
Severity: Critical
Advisory: CVE-2025-71068
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-01-13
Source: https://osv.dev/vulnerability/CVE-2025-71068
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.11.0 <5.15.198, >=5.16.0 <6.6.120, >=6.7.0 <6.12.64, >=6.13.0 <6.18.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

svcrdma: bound check rq_pages index in inline path

svc_rdma_copy_inline_range indexed rqstp->rq_pages[rc_curpage] without
verifying rc_curpage stays within the allocated page array. Add guards
before the first use and after advancing to a new page.

## References
- https://git.kernel.org/stable/c/5f140b525180c628db8fa6c897f138194a2de417
- https://git.kernel.org/stable/c/7ba826aae1d43212f3baa53a2175ad949e21926e
- https://git.kernel.org/stable/c/a22316f5e9a29e4b92030bd8fb9435fe0eb1d5c9
- https://git.kernel.org/stable/c/d1bea0ce35b6095544ee82bb54156fc62c067e58
- https://git.kernel.org/stable/c/da1ccfc4c452541584a4eae89e337cfa21be6d5a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/71xxx/CVE-2025-71068.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-71068
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
