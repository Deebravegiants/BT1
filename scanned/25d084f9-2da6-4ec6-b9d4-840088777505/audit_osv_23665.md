# [M] staging: rtl8712: fix a potential memory leak in r871xu_drv_init()

## Summary
Severity: Medium
Advisory: CVE-2022-49312
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49312
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.37 <5.10.122, >=5.11.0 <5.15.47, >=5.16.0 <5.17.15, >=5.18.0 <5.18.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

staging: rtl8712: fix a potential memory leak in r871xu_drv_init()

In r871xu_drv_init(), if r8712_init_drv_sw() fails, then the memory
allocated by r8712_alloc_io_queue() in r8712_usb_dvobj_init() is not
properly released as there is no action will be performed by
r8712_usb_dvobj_deinit().
To properly release it, we should call r8712_free_io_queue() in
r8712_usb_dvobj_deinit().

Besides, in r871xu_dev_remove(), r8712_usb_dvobj_deinit() will be called
by r871x_dev_unload() under condition `padapter->bup` and
r8712_free_io_queue() is called by r8712_free_drv_sw().
However, r8712_usb_dvobj_deinit() does not rely on `padapter->bup` and
calling r8712_free_io_queue() in r8712_free_drv_sw() is negative for
better understading the code.
So I move r8712_usb_dvobj_deinit() into r871xu_dev_remove(), and remove
r8712_free_io_queue() from r8712_free_drv_sw().

## References
- https://git.kernel.org/stable/c/205e039fead72e87ad2838f5e649a4c4834f648b
- https://git.kernel.org/stable/c/5a89a92efc342dd7c44b6056da87debc598f9c73
- https://git.kernel.org/stable/c/7288ff561de650d4139fab80e9cb0da9b5b32434
- https://git.kernel.org/stable/c/8eb42d6d10f8fe509117859defddf9e72b4fa4d0
- https://git.kernel.org/stable/c/a2882b8baad068d21c99fb2ab5a85a2bdbd5b834
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49312.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49312
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
