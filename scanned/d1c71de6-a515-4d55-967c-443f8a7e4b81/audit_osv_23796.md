# [M] drm/msm/hdmi: check return value after calling platform_get_resource_byname()

## Summary
Severity: Medium
Advisory: CVE-2022-49495
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49495
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.3.0 <4.9.318, >=4.10.0 <4.14.283, >=4.15.0 <4.19.247, >=4.20.0 <5.4.198, >=5.5.0 <5.10.121, >=5.11.0 <5.15.46, >=5.16.0 <5.17.14, >=5.18.0 <5.18.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/msm/hdmi: check return value after calling platform_get_resource_byname()

It will cause null-ptr-deref if platform_get_resource_byname() returns NULL,
we need check the return value.

Patchwork: https://patchwork.freedesktop.org/patch/482992/

## References
- https://git.kernel.org/stable/c/0978fcce91b90b561b8c82e7c492ba9fc8440eef
- https://git.kernel.org/stable/c/2b3ed7547b1a052209da6c4ab886ffe0eed88c42
- https://git.kernel.org/stable/c/4cd66a8016b872a153bf892fe4258cbc0dacf5b1
- https://git.kernel.org/stable/c/6369dda4a2209142ab819f01d3d2076d81e3ebdd
- https://git.kernel.org/stable/c/9cb1ee33efccb8b107ee04b7b3441820de3fd2da
- https://git.kernel.org/stable/c/9f5495a5c51c1d11c6ffc13aa2befffec0c2651a
- https://git.kernel.org/stable/c/a36e506711548df923ceb7ec9f6001375be799a5
- https://git.kernel.org/stable/c/c1bfacf0daf25a5fc7d667399d6ff2dffda84cd8
- https://git.kernel.org/stable/c/d9cb951d11a4ace4de5c50b1178ad211de17079e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49495.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49495
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
