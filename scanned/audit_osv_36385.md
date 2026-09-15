# [H] drm/vmwgfx: Return the correct value in vmw_translate_ptr functions

## Summary
Severity: High
Advisory: CVE-2026-23317
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-03-25
Source: https://osv.dev/vulnerability/CVE-2026-23317
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.1.167, >=6.2.0 <6.12.77, >=6.7.0 <6.18.17, >=6.13.0 <6.19.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/vmwgfx: Return the correct value in vmw_translate_ptr functions

Before the referenced fixes these functions used a lookup function that
returned a pointer. This was changed to another lookup function that
returned an error code with the pointer becoming an out parameter.

The error path when the lookup failed was not changed to reflect this
change and the code continued to return the PTR_ERR of the now
uninitialized pointer. This could cause the vmw_translate_ptr functions
to return success when they actually failed causing further uninitialized
and OOB accesses.

## References
- https://git.kernel.org/stable/c/149f028772fa2879d9316b924ce948a6a0877e45
- https://git.kernel.org/stable/c/36cb28b6d303a81e6ed4536017090e85e0143e42
- https://git.kernel.org/stable/c/5023ca80f9589295cb60735016e39fc5cc714243
- https://git.kernel.org/stable/c/531f45589787799aa81b63e1e1f8e71db5d93dd1
- https://git.kernel.org/stable/c/7e55d0788b362c93660b80cc5603031bbbdefa98
- https://git.kernel.org/stable/c/ce3a5cf139787c186d5d54336107298cacaad2b9
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23317.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-23317
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
