# [H] drm/amdgpu: Fix context pstate override handling

## Summary
Severity: High
Advisory: CVE-2026-68273
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68273
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.1.0 <6.12.103, >=6.13.0 <6.18.44, >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amdgpu: Fix context pstate override handling

There are several problems in the context pstate handling code.

The most serious ones are potential use-after-free and NULL pointer
dereferences at context initialization time. Both are due
amdgpu_ctx_init() not holding the adev->pm.stable_pstate_ctx_lock, which
is otherwise used from both sysfs and the context code itself for
modifying and clearing the stored context pointer.

Second issue is that context fini can trample over the pstate
configuration set via sysfs. This is due the restore state
(ctx->stable_pstate) being saved at context init time, and not if, or when
the context actually changes the pstate. As the context exits it will
therefore incorrectly restore to what was set before the sysfs override
was requested.

The simplest fix is to drastically simplify how the state is tracked, by
clearly defining the points at which pstate ownership is taken and
released, and to handle all transitions under the correct lock.

Instead of at context init time, the previous state is saved only at the
point the context overrides the current state, and is restored on context
exit only if the context is still the owner of the current override state.

(cherry picked from commit 1b5e413713c0a93bc1818394d0ce49aaad21bd27)

## References
- https://git.kernel.org/stable/c/23a8726e1d7597fe7c9a59d5dc42ba8b7d345b8a
- https://git.kernel.org/stable/c/9f9c88eb298c54348be3ca4087f4f4c615065b87
- https://git.kernel.org/stable/c/c1dc4ccb82c9e56325d8e7514ca4c90bd1efb351
- https://git.kernel.org/stable/c/e06c39cc1c48dca68a5ffd971c23025a52d46634
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68273.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68273
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
