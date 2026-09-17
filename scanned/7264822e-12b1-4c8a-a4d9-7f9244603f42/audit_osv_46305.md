# [H] drm/amdgpu: Fix possible null pointer dereference

## Summary
Severity: High
Advisory: CVE-2023-52883
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-06-20
Source: https://osv.dev/vulnerability/CVE-2023-52883
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.4.0 <6.5.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amdgpu: Fix possible null pointer dereference

abo->tbo.resource may be NULL in amdgpu_vm_bo_update.

## References
- https://git.kernel.org/stable/c/51b79f33817544e3b4df838d86e8e8e4388ff684
- https://git.kernel.org/stable/c/fefac8c4686fd81fde6830c6dae32f9001d2ac28
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52883.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52883
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
