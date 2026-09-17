# [H] gpio: virtuser: fix missing lookup table cleanups

## Summary
Severity: High
Advisory: CVE-2025-21661
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-01-21
Source: https://osv.dev/vulnerability/CVE-2025-21661
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.11.0 <6.12.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

gpio: virtuser: fix missing lookup table cleanups

When a virtuser device is created via configfs and the probe fails due
to an incorrect lookup table, the table is not removed. This prevents
subsequent probe attempts from succeeding, even if the issue is
corrected, unless the device is released. Additionally, cleanup is also
needed in the less likely case of platform_device_register_full()
failure.

Besides, a consistent memory leak in lookup_table->dev_id was spotted
using kmemleak by toggling the live state between 0 and 1 with a correct
lookup table.

Introduce gpio_virtuser_remove_lookup_table() as the counterpart to the
existing gpio_virtuser_make_lookup_table() and call it from all
necessary points to ensure proper cleanup.

## References
- https://git.kernel.org/stable/c/a619cba8c69c434258ff4101d463322cd63e1bdc
- https://git.kernel.org/stable/c/d72d0126b1f6981f6ce8b4247305f359958c11b5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21661.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21661
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
