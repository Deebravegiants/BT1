# [H] drm/amdgpu: avoid double drm_exec_fini() in userq validate

## Summary
Severity: High
Advisory: CVE-2026-52987
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-52987
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.19.0 <7.0.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amdgpu: avoid double drm_exec_fini() in userq validate

When new_addition is true, amdgpu_userq_vm_validate() calls
drm_exec_fini(&exec) before iterating over the collected HMM ranges and
calling amdgpu_ttm_tt_get_user_pages().

If amdgpu_ttm_tt_get_user_pages() fails in that path, the code jumps to
unlock_all and calls drm_exec_fini(&exec) a second time on the same
exec object. drm_exec_fini() is not idempotent: it frees exec->objects
and may also drop exec->contended and finalize the ww acquire context.

Route that error path directly to the range cleanup once exec has
already been finalized.

Issue found using a prototype static analysis tool
and confirmed by code review.

(cherry picked from commit 2802952e4a07306da6ebe813ff1acacc5691851a)

## References
- https://git.kernel.org/stable/c/508babf310365f1107a2e8831c267c292a286818
- https://git.kernel.org/stable/c/c7c3ae7c01e5a0742b93cb9b40800bdd7f811e38
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-52987.json
- https://access.redhat.com/security/cve/CVE-2026-52987
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/52xxx/CVE-2026-52987.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-52987
- https://bugzilla.redhat.com/show_bug.cgi?id=2492365
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
