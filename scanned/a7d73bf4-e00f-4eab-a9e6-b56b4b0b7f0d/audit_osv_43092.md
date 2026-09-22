# [H] drm/amdkfd: fix list_del corruption in kfd_criu_resume_svm

## Summary
Severity: High
Advisory: CVE-2026-72449
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72449
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.18.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amdkfd: fix list_del corruption in kfd_criu_resume_svm

The cleanup tail of kfd_criu_resume_svm() walks
svms->criu_svm_metadata_list and kfree()s each struct criu_svm_metadata
without removing it from the list. The list head is left pointing at
freed kmalloc-96 objects.

A second AMDKFD_IOC_CRIU_OP from the same process re-enters: list_empty()
reads the dangling ->next (use-after-free), the loop walks freed entries,
and each is kfree()'d again (double-free). This is reachable by an
unprivileged render-group user via /dev/kfd with no capabilities required.

Add list_del() before the kfree() so the list is properly emptied. The
list_for_each_entry_safe() iterator already caches the next pointer, so
unlinking during the walk is safe.

(cherry picked from commit 6322d278a298e2c1430b9d2697743d3a04b788b1)

## References
- https://git.kernel.org/stable/c/506e635aed05dbdeef11e3c59f6e42980cda5b6d
- https://git.kernel.org/stable/c/838b57b3e7ce8cce0fda56d0861add3d464dd6c8
- https://git.kernel.org/stable/c/8fa5655da368d0306c03e9dc9cda8ae2a7840926
- https://git.kernel.org/stable/c/96ac562a9ea3020981f536384711190841c81aa8
- https://git.kernel.org/stable/c/c8a8d350a273c005a48c64c4519d21b2a51c5ceb
- https://git.kernel.org/stable/c/e33a3bd5cb8d0cf1557dee014115f812c9686130
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72449.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72449
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
