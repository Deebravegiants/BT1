# [H] drm/xe/pf: Fix use-after-free in migration restore

## Summary
Severity: High
Advisory: CVE-2026-31490
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-22
Source: https://osv.dev/vulnerability/CVE-2026-31490
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.19.0 <6.19.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/xe/pf: Fix use-after-free in migration restore

When an error is returned from xe_sriov_pf_migration_restore_produce(),
the data pointer is not set to NULL, which can trigger use-after-free
in subsequent .write() calls.
Set the pointer to NULL upon error to fix the problem.

(cherry picked from commit 4f53d8c6d23527d734fe3531d08e15cb170a0819)

## References
- https://git.kernel.org/stable/c/87997b6c6516e049cbaf2fc6810b213d587a06b1
- https://git.kernel.org/stable/c/e28552b4ddea5cb4725380dd08237831af835124
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31490.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31490
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
