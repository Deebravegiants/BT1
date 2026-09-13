# [H] drm/xe/guc_submit: add missing locking in wedged_fini

## Summary
Severity: High
Advisory: CVE-2024-49943
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-10-21
Source: https://osv.dev/vulnerability/CVE-2024-49943
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.11.0 <6.11.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/xe/guc_submit: add missing locking in wedged_fini

Any non-wedged queue can have a zero refcount here and can be running
concurrently with an async queue destroy, therefore dereferencing the
queue ptr to check wedge status after the lookup can trigger UAF if
queue is not wedged.  Fix this by keeping the submission_state lock held
around the check to postpone the free and make the check safe, before
dropping again around the put() to avoid the deadlock.

(cherry picked from commit d28af0b6b9580b9f90c265a7da0315b0ad20bbfd)

## References
- https://git.kernel.org/stable/c/790533e44bfc7af929842fccd9674c9f424d4627
- https://git.kernel.org/stable/c/d88f9bab7e62dd0dbe983fa70cf040042a60cc84
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/49xxx/CVE-2024-49943.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-49943
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
