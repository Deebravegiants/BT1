# [H] bus: fsl-mc-bus: fix KASAN use-after-free in fsl_mc_bus_remove()

## Summary
Severity: High
Advisory: CVE-2022-49711
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49711
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.8.0 <5.10.248, >=5.11.0 <5.15.49, >=5.16.0 <5.18.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

bus: fsl-mc-bus: fix KASAN use-after-free in fsl_mc_bus_remove()

In fsl_mc_bus_remove(), mc->root_mc_bus_dev->mc_io is passed to
fsl_destroy_mc_io(). However, mc->root_mc_bus_dev is already freed in
fsl_mc_device_remove(). Then reference to mc->root_mc_bus_dev->mc_io
triggers KASAN use-after-free. To avoid the use-after-free, keep the
reference to mc->root_mc_bus_dev->mc_io in a local variable and pass to
fsl_destroy_mc_io().

This patch needs rework to apply to kernels older than v5.15.

## References
- https://git.kernel.org/stable/c/161b68b0a728377aaa10a8e14c70e7734f3c9ff7
- https://git.kernel.org/stable/c/720ab105df7bf3eee62d2bddd41526b29d07d045
- https://git.kernel.org/stable/c/928ea98252ad75118950941683893cf904541da9
- https://git.kernel.org/stable/c/ccd1751092341ac120a961835211f9f2e3735963
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49711.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49711
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
