# [H] RDMA/cxgb4: Fix potential null-ptr-deref in pass_establish()

## Summary
Severity: High
Advisory: CVE-2023-53335
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-17
Source: https://osv.dev/vulnerability/CVE-2023-53335
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.7.0 <5.15.99, >=5.16.0 <6.1.16, >=6.2.0 <6.2.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

RDMA/cxgb4: Fix potential null-ptr-deref in pass_establish()

If get_ep_from_tid() fails to lookup non-NULL value for ep, ep is
dereferenced later regardless of whether it is empty.
This patch adds a simple sanity check to fix the issue.

Found by Linux Verification Center (linuxtesting.org) with SVACE.

## References
- https://git.kernel.org/stable/c/283861a4c52c1ea4df3dd1b6fc75a50796ce3524
- https://git.kernel.org/stable/c/2cfc00e974d75a3aa8155f2660f57d342e1f67ca
- https://git.kernel.org/stable/c/9dca64042d855a24b0bd81ce242e5dc7e939f6eb
- https://git.kernel.org/stable/c/9ddc77eefb2a567b705c3c86ab2ddabe43cadf1b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53335.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53335
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
