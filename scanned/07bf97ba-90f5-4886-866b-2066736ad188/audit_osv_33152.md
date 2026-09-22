# [M] drm/xe/vm: Clear the scratch_pt pointer on error

## Summary
Severity: Medium
Advisory: CVE-2025-39811
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-16
Source: https://osv.dev/vulnerability/CVE-2025-39811
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.8.0 <6.12.45, >=6.13.0 <6.16.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/xe/vm: Clear the scratch_pt pointer on error

Avoid triggering a dereference of an error pointer on cleanup in
xe_vm_free_scratch() by clearing any scratch_pt error pointer.

(cherry picked from commit 358ee50ab565f3c8ea32480e9d03127a81ba32f8)

## References
- https://git.kernel.org/stable/c/2b55ddf36229e0278c956215784ab1feeff510aa
- https://git.kernel.org/stable/c/84603ed1d73ebb8de856dc11f4f5d3541c48f7a2
- https://git.kernel.org/stable/c/c8277d229c7840e8090d4704e50f2ca014d194c7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39811.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39811
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
