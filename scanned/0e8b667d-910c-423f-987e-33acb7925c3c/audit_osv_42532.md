# [H] drm/xe/guc: Keep scheduler timeline name alive

## Summary
Severity: High
Advisory: CVE-2026-68383
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68383
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.17.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/xe/guc: Keep scheduler timeline name alive

The scheduler keeps a pointer to the timeline name, but q->name
is freed with the exec queue while scheduler fences can still
reference it.

Store the name in struct xe_guc_exec_queue so it shares
the scheduler's RCU-deferred lifetime.

(cherry picked from commit 41075f0eb5dcbd3b065d15f15ef7bbe9315188e8)

## References
- https://git.kernel.org/stable/c/299bc6d50b1bed7d1f408391736712f01a0855e2
- https://git.kernel.org/stable/c/77fd62412431e8c80ef2ad61466bc76fe425f80a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68383.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68383
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
