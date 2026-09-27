# [H] staging: media: ipu7: fix double-free and use-after-free in error paths

## Summary
Severity: High
Advisory: CVE-2026-64447
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-25
Source: https://osv.dev/vulnerability/CVE-2026-64447
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.17.0 <6.18.39, >=6.19.0 <7.1.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

staging: media: ipu7: fix double-free and use-after-free in error paths

In both ipu7_isys_init() and ipu7_psys_init(), pdata is allocated and
then passed to ipu7_bus_initialize_device(), which stores it in
adev->pdata. The ipu7_bus_release() function frees adev->pdata when the
device's reference count drops to zero.

Two error paths incorrectly call kfree(pdata) after the device teardown
has already freed it:

1. When ipu7_mmu_init() fails: put_device() is called, which drops the
   reference count to zero and triggers ipu7_bus_release() ->
   kfree(pdata). The subsequent kfree(pdata) is a double-free.

2. When ipu7_bus_add_device() fails: it calls auxiliary_device_uninit()
   internally, which calls put_device() -> ipu7_bus_release() ->
   kfree(pdata). The subsequent kfree(pdata) is again a double-free.

Note that the kfree(pdata) when ipu7_bus_initialize_device() itself
fails is correct, because in that case auxiliary_device_init() failed
and the release function was never set up, so pdata must be freed
manually.

Additionally, the error code was not saved before calling put_device(),
causing ERR_CAST() to dereference the already-freed adev pointer when
constructing the return value. Fix this by saving the error from
dev_err_probe() before put_device() and returning ERR_PTR() instead.

Remove the redundant kfree(pdata) calls and fix the use-after-free in
the return values of the two affected error paths.

## References
- https://git.kernel.org/stable/c/837c1f9655421055f751ed34745e820a54a27642
- https://git.kernel.org/stable/c/b5ddc7257bee71f5b8cf9083e2b0ac0427e9fbb3
- https://git.kernel.org/stable/c/d3a9a8cf2d7fd61a2f63df61f6cbc0a9bb007cc0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64447.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64447
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
