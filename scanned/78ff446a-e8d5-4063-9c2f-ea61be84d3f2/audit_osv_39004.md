# [H] thermal: core: Fix thermal zone device registration error path

## Summary
Severity: High
Advisory: CVE-2026-43332
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-08
Source: https://osv.dev/vulnerability/CVE-2026-43332
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.6.134, >=6.7.0 <6.12.81, >=6.8.0 <6.18.22, >=6.13.0 <6.19.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

thermal: core: Fix thermal zone device registration error path

If thermal_zone_device_register_with_trips() fails after registering
a thermal zone device, it needs to wait for the tz->removal completion
like thermal_zone_device_unregister(), in case user space has managed
to take a reference to the thermal zone device's kobject, in which case
thermal_release() may not be called by the error path itself and tz may
be freed prematurely.

Add the missing wait_for_completion() call to the thermal zone device
registration error path.

## References
- https://git.kernel.org/stable/c/4d390f0e507dfb16d58f83a58d78d1150dc8b9d7
- https://git.kernel.org/stable/c/604da9c04c218362e1c1457304ebeb9c199d537c
- https://git.kernel.org/stable/c/9e07e3b81807edd356e1f794cffa00a428eff443
- https://git.kernel.org/stable/c/9e796001af97a1f7368d5114b7a8533dd98d797a
- https://git.kernel.org/stable/c/c4c7219e93319bba9ba0765dee597784c78f63c5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43332.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43332
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
