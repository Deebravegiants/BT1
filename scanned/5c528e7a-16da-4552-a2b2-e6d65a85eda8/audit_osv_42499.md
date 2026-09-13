# [H] drm/xe/vm: Fix SVM leak on resv obj alloc failure in xe_vm_create()

## Summary
Severity: High
Advisory: CVE-2026-68298
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68298
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.18.0 <6.18.42, >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/xe/vm: Fix SVM leak on resv obj alloc failure in xe_vm_create()

Commit 9e9787414882 ("drm/xe/userptr: replace xe_hmm with gpusvm") made
xe_svm_init() unconditional in xe_vm_create() and extended it to also
initialize a "simple" gpusvm state for non-fault-mode VMs. The matching
xe_svm_fini() call in xe_vm_close_and_put() was updated to run
unconditionally, but the error unwind path in xe_vm_create() was not.

On the drm_gpuvm_resv_object_alloc() failure path, xe_svm_init() has
already succeeded but xe_svm_fini() is only called when
XE_VM_FLAG_FAULT_MODE is set. For non-fault-mode VMs this leaves
vm->svm.gpusvm partially initialized and leaks the resources allocated
by drm_gpusvm_init().

For fault-mode VMs, xe_svm_init() additionally acquires the pagemap
owner via drm_pagemap_acquire_owner() and the pagemaps via
xe_svm_get_pagemaps(). Those resources are released by xe_svm_close(),
not xe_svm_fini(). On the same error path, xe_svm_close() is not
called either, so fault-mode VMs leak the pagemap owner and pagemaps.

Fix both leaks:

- Call xe_svm_fini() unconditionally on the err_svm_fini path, matching
  the unconditional xe_svm_init() call. Move the vm->size = 0
  assignment out of the conditional so the xe_vm_is_closed() assert in
  xe_svm_fini() (and xe_svm_close()) holds for both modes.

- Call xe_svm_close() for fault-mode VMs before xe_svm_fini(), matching
  the ordering used in xe_vm_close_and_put().

(cherry picked from commit ca2a3587d577ba764e0fe628fb676244fc33ddd4)

## References
- https://git.kernel.org/stable/c/279339aa8bdcf9db40094cf2bcbd495c53dbe817
- https://git.kernel.org/stable/c/9ac92736030f3395d970c300eaeb59ac258a0c3e
- https://git.kernel.org/stable/c/d2c6800ad1802bed72a6de1416536737f114f1d6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68298.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68298
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
