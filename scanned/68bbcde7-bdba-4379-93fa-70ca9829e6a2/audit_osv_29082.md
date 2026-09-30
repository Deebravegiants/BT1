# [H] drm/i915/hwmon: Get rid of devm

## Summary
Severity: High
Advisory: CVE-2024-39479
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-07-05
Source: https://osv.dev/vulnerability/CVE-2024-39479
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.2.0 <6.6.34, >=6.7.0 <6.9.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/i915/hwmon: Get rid of devm

When both hwmon and hwmon drvdata (on which hwmon depends) are device
managed resources, the expectation, on device unbind, is that hwmon will be
released before drvdata. However, in i915 there are two separate code
paths, which both release either drvdata or hwmon and either can be
released before the other. These code paths (for device unbind) are as
follows (see also the bug referenced below):

Call Trace:
release_nodes+0x11/0x70
devres_release_group+0xb2/0x110
component_unbind_all+0x8d/0xa0
component_del+0xa5/0x140
intel_pxp_tee_component_fini+0x29/0x40 [i915]
intel_pxp_fini+0x33/0x80 [i915]
i915_driver_remove+0x4c/0x120 [i915]
i915_pci_remove+0x19/0x30 [i915]
pci_device_remove+0x32/0xa0
device_release_driver_internal+0x19c/0x200
unbind_store+0x9c/0xb0

and

Call Trace:
release_nodes+0x11/0x70
devres_release_all+0x8a/0xc0
device_unbind_cleanup+0x9/0x70
device_release_driver_internal+0x1c1/0x200
unbind_store+0x9c/0xb0

This means that in i915, if use devm, we cannot gurantee that hwmon will
always be released before drvdata. Which means that we have a uaf if hwmon
sysfs is accessed when drvdata has been released but hwmon hasn't.

The only way out of this seems to be do get rid of devm_ and release/free
everything explicitly during device unbind.

v2: Change commit message and other minor code changes
v3: Cleanup from i915_hwmon_register on error (Armin Wolf)
v4: Eliminate potential static analyzer warning (Rodrigo)
    Eliminate fetch_and_zero (Jani)
v5: Restore previous logic for ddat_gt->hwmon_dev error return (Andi)

## References
- https://git.kernel.org/stable/c/5bc9de065b8bb9b8dd8799ecb4592d0403b54281
- https://git.kernel.org/stable/c/ce5a22d22db691d14516c3b8fdbf69139eb2ea8f
- https://git.kernel.org/stable/c/cfa73607eb21a4ce1d6294a2c5733628897b48a2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/39xxx/CVE-2024-39479.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-39479
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
