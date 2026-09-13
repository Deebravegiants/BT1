# [C] svcrdma: use rc_pageoff for memcpy byte offset

## Summary
Severity: Critical
Advisory: CVE-2025-68811
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-01-13
Source: https://osv.dev/vulnerability/CVE-2025-68811
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.8.0 <6.12.64, >=6.13.0 <6.18.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

svcrdma: use rc_pageoff for memcpy byte offset

svc_rdma_copy_inline_range added rc_curpage (page index) to the page
base instead of the byte offset rc_pageoff. Use rc_pageoff so copies
land within the current page.

Found by ZeroPath (https://zeropath.com)

## References
- https://git.kernel.org/stable/c/2a77c8dd49bccf0ca232be7c836cec1209abb8da
- https://git.kernel.org/stable/c/a8ee9099f30654917aa68f55d707b5627e1dbf77
- https://git.kernel.org/stable/c/e8623e9c451e23d84b870811f42fd872b4089ef6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/68xxx/CVE-2025-68811.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-68811
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
