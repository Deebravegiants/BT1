# [H] thermal: of: fix double-free on unregistration

## Summary
Severity: High
Advisory: CVE-2023-53997
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-24
Source: https://osv.dev/vulnerability/CVE-2023-53997
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.4.0 <6.4.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

thermal: of: fix double-free on unregistration

Since commit 3d439b1a2ad3 ("thermal/core: Alloc-copy-free the thermal
zone parameters structure"), thermal_zone_device_register() allocates
a copy of the tzp argument and frees it when unregistering, so
thermal_of_zone_register() now ends up leaking its original tzp and
double-freeing the tzp copy. Fix this by locating tzp on stack instead.

## References
- https://git.kernel.org/stable/c/ac4436a5b20e0ef1f608a9ef46c08d5d142f8da6
- https://git.kernel.org/stable/c/adce49089412a9ae28f5c666e0bb12fbcd86b3f7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53997.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53997
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
