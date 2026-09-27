# [H] drm/amdgpu: Fix integer overflow in amdgpu_cs_pass1

## Summary
Severity: High
Advisory: CVE-2023-53707
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-22
Source: https://osv.dev/vulnerability/CVE-2023-53707
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.2.0 <6.1.47, >=6.2.0 <6.4.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amdgpu: Fix integer overflow in amdgpu_cs_pass1

The type of size is unsigned int, if size is 0x40000000, there will
be an integer overflow, size will be zero after size *= sizeof(uint32_t),
will cause uninitialized memory to be referenced later.

## References
- https://git.kernel.org/stable/c/87c2213e85bd81e4a9a4d0880c256568794ae388
- https://git.kernel.org/stable/c/9f55d300541cb5b435984d269087810581580b00
- https://git.kernel.org/stable/c/c3deb091398e9e469d08dd1599b6d76fd6b29df8
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53707.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53707
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
