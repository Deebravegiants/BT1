# [H] gfs2: fix double destroy_workqueue error

## Summary
Severity: High
Advisory: CVE-2024-49956
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2024-10-21
Source: https://osv.dev/vulnerability/CVE-2024-49956
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.11.0 <6.11.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

gfs2: fix double destroy_workqueue error

When gfs2_fill_super() fails, destroy_workqueue() is called within
gfs2_gl_hash_clear(), and the subsequent code path calls
destroy_workqueue() on the same work queue again.

This issue can be fixed by setting the work queue pointer to NULL after
the first destroy_workqueue() call and checking for a NULL pointer
before attempting to destroy the work queue again.

## References
- https://git.kernel.org/stable/c/6cb9df81a2c462b89d2f9611009ab43ae8717841
- https://git.kernel.org/stable/c/a5336035728d77efd76306940d742a6f23debe68
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/49xxx/CVE-2024-49956.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-49956
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
