# [H] drm/msm: make sure last_fence is always updated

## Summary
Severity: High
Advisory: CVE-2025-68314
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2025-12-16
Source: https://osv.dev/vulnerability/CVE-2025-68314
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.17.0 <6.17.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/msm: make sure last_fence is always updated

Update last_fence in the vm-bind path instead of kernel managed path.

last_fence is used to wait for work to finish in vm_bind contexts but not
used for kernel managed contexts.

This fixes a bug where last_fence is not waited on context close leading
to faults as resources are freed while in use.

Patchwork: https://patchwork.freedesktop.org/patch/680080/

## References
- https://git.kernel.org/stable/c/86404a9e3013d814a772ac407573be5d3cd4ee0d
- https://git.kernel.org/stable/c/8ee817ceafba266d9c6f3a09babd2ac7441d9a2b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/68xxx/CVE-2025-68314.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-68314
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
