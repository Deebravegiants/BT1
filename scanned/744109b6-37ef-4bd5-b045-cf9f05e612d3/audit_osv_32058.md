# [M] thermal: int340x: Add NULL check for adev

## Summary
Severity: Medium
Advisory: CVE-2025-23136
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-04-16
Source: https://osv.dev/vulnerability/CVE-2025-23136
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.18.0 <5.4.292, >=5.5.0 <5.10.236, >=5.11.0 <5.15.180, >=5.16.0 <6.1.134, >=6.2.0 <6.6.87, >=6.7.0 <6.12.23, >=6.13.0 <6.13.11, >=6.14.0 <6.14.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

thermal: int340x: Add NULL check for adev

Not all devices have an ACPI companion fwnode, so adev might be NULL.
This is similar to the commit cd2fd6eab480
("platform/x86: int3472: Check for adev == NULL").

Add a check for adev not being set and return -ENODEV in that case to
avoid a possible NULL pointer deref in int3402_thermal_probe().

Note, under the same directory, int3400_thermal_probe() has such a
check.

[ rjw: Subject edit, added Fixes: ]

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://git.kernel.org/stable/c/0c49f12c77b77a706fd41370c11910635e491845
- https://git.kernel.org/stable/c/2542a3f70e563a9e70e7ded314286535a3321bdb
- https://git.kernel.org/stable/c/3155d5261b518776d1b807d9d922669991bbee56
- https://git.kernel.org/stable/c/6a810c462f099353e908c70619638884cb82229c
- https://git.kernel.org/stable/c/8e8f1ddf4186731649df8bc9646017369eb19186
- https://git.kernel.org/stable/c/953d28a4f459fcbde2d08f51aeca19d6b0f179f3
- https://git.kernel.org/stable/c/ac2eb7378319e3836cdf3a2c15a0bdf04c50e81d
- https://git.kernel.org/stable/c/bc7b5f782d28942dbdfda70df30ce132694a06de
- https://git.kernel.org/stable/c/d0d21c8e44216fa9afdb3809edf213f3c0a8c060
- https://lists.debian.org/debian-lts-announce/2025/05/msg00030.html
- https://lists.debian.org/debian-lts-announce/2025/05/msg00045.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/23xxx/CVE-2025-23136.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-23136
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
