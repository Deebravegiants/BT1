# [H] drm/amdgpu: fix lifetime issue of amdgpu_vm_get_task_info_pasid()

## Summary
Severity: High
Advisory: CVE-2026-68245
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68245
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.9.0 <6.12.101, >=6.13.0 <6.18.42, >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amdgpu: fix lifetime issue of amdgpu_vm_get_task_info_pasid()

The vm pointer returned from amdgpu_vm_get_vm_from_pasid() is only
valid while the lock is still being held. Once xa_unlock_irqrestore is
called and returned, the pointer is no longer under lock and is subject
to modification. Since, the caller still dereferences vm->task_info in
amdgpu_vm_get_task_info_vm() after the lock is removed, this causes a
use after unlock problem.

Remove the lifetime issue present in amdgpu_vm_get_task_info_pasid()
through removing the amdgpu_vm_get_vm_from_pasid() function from
amdgpu_vm.c and making the relevant code inline to hold the lock while
it is still in use.

(cherry picked from commit 9d01579f3f868b333acc901815972685989092c7)

## References
- https://git.kernel.org/stable/c/04cc4aa3617b0ed67e859f91f09de5d896a46f3a
- https://git.kernel.org/stable/c/1173190412fb9d12e7efce76734118d9712ff970
- https://git.kernel.org/stable/c/5d5fb9124a2bba96a7807086d8fe0f7ce810d546
- https://git.kernel.org/stable/c/fe16a7e5336ae888751984e30c451fbf7cfa5df7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68245.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68245
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
