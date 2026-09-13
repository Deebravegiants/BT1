# [H] drm/xe: fix UAF around queue destruction

## Summary
Severity: High
Advisory: CVE-2024-49876
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-10-21
Source: https://osv.dev/vulnerability/CVE-2024-49876
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.8.0 <6.10.14, >=6.11.0 <6.11.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/xe: fix UAF around queue destruction

We currently do stuff like queuing the final destruction step on a
random system wq, which will outlive the driver instance. With bad
timing we can teardown the driver with one or more work workqueue still
being alive leading to various UAF splats. Add a fini step to ensure
user queues are properly torn down. At this point GuC should already be
nuked so queue itself should no longer be referenced from hw pov.

v2 (Matt B)
 - Looks much safer to use a waitqueue and then just wait for the
   xa_array to become empty before triggering the drain.

(cherry picked from commit 861108666cc0e999cffeab6aff17b662e68774e3)

## References
- https://git.kernel.org/stable/c/272b0e78874586d6ccae04079d75b27b47705544
- https://git.kernel.org/stable/c/2d2be279f1ca9e7288282d4214f16eea8a727cdb
- https://git.kernel.org/stable/c/421c74670b0f9d5c007f1276d3647aa58f407fde
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/49xxx/CVE-2024-49876.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-49876
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
