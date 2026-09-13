# [H] amdkfd: properly free gang_ctx_bo when failed to init user queue

## Summary
Severity: High
Advisory: CVE-2025-21842
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-03-07
Source: https://osv.dev/vulnerability/CVE-2025-21842
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.12.0 <6.12.16, >=6.13.0 <6.13.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

amdkfd: properly free gang_ctx_bo when failed to init user queue

The destructor of a gtt bo is declared as
void amdgpu_amdkfd_free_gtt_mem(struct amdgpu_device *adev, void **mem_obj);
Which takes void** as the second parameter.

GCC allows passing void* to the function because void* can be implicitly
casted to any other types, so it can pass compiling.

However, passing this void* parameter into the function's
execution process(which expects void** and dereferencing void**)
will result in errors.

## References
- https://git.kernel.org/stable/c/091a68c58c1bbd2ab7d05d1b32c1306394ec691d
- https://git.kernel.org/stable/c/a33f7f9660705fb2ecf3467b2c48965564f392ce
- https://git.kernel.org/stable/c/ae5ab1c1ae504f622cc1ff48830a9ed48428146d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21842.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21842
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
