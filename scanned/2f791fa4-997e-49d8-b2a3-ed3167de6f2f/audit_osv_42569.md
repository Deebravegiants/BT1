# [H] drm/amdkfd: clamp v9 CRIU control stack checkpoint copy to BO size

## Summary
Severity: High
Advisory: CVE-2026-68447
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-08-12
Source: https://osv.dev/vulnerability/CVE-2026-68447
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.18.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amdkfd: clamp v9 CRIU control stack checkpoint copy to BO size

CRIU checkpoint copies the MQD control stack using cp_hqd_cntl_stack_size
from hardware without bounding it to the allocated BO region. If the HW
field is larger than the queue's control stack allocation, memcpy reads
past the BO into adjacent GTT memory and can leak kernel data to userspace.

Store the page-aligned control stack BO size in mqd_manager and clamp
checkpoint copies and reported checkpoint sizes to
min(cp_hqd_cntl_stack_size, mm->ctl_stack_size). Apply the same bound
for multi-XCC v9.4.3 checkpoint layout.

(cherry picked from commit 6c2abd0ec09e86c6323010673766f76050e28aa3)

## References
- https://git.kernel.org/stable/c/426ffae6ecc7ec77d32bf8be065c21a1b881b084
- https://git.kernel.org/stable/c/a0d87beb2660a5098b2b0ecdc1e96810a9074ea9
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68447.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68447
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
