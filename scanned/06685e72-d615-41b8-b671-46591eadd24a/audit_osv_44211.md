# [H] hwmon: (asus_atk0110) Check package count before accessing element

## Summary
Severity: High
Advisory: CVE-2026-80593
Ecosystem: Linux
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-28
Source: https://osv.dev/vulnerability/CVE-2026-80593
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.32 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

hwmon: (asus_atk0110) Check package count before accessing element

atk_ec_present() walks the management group package returned by the GGRP
ACPI method and, for each sub-package, reads its first element:

	id = &obj->package.elements[0];
	if (id->type != ACPI_TYPE_INTEGER)

without checking that the sub-package is non-empty.  ACPICA allocates the
element array with exactly package.count entries, so for a sub-package
with a zero count this reads past the allocation.

The sibling function atk_debugfs_ggrp_open() performs the same access but
skips empty packages with a package.count check first.  Add the same
check to atk_ec_present() so a malformed firmware package cannot trigger
an out-of-bounds read.

## References
- https://git.kernel.org/stable/c/2a137124664aad1e36d8d74e8e2207365a04737f
- https://git.kernel.org/stable/c/459b0a0439ea65b2b612aa572eb62a2e26d05618
- https://git.kernel.org/stable/c/76392d35c8df471b288cfc6536bd092b3c8ee2cf
- https://git.kernel.org/stable/c/768f20e7bb48d723b82cb142120263d0806fbeb8
- https://git.kernel.org/stable/c/981a8a2e3773dc7e704943388a1fb97970b23275
- https://git.kernel.org/stable/c/b770fcfcdced569bcf7c6982aeea8c3d11a21c2b
- https://git.kernel.org/stable/c/d8d4fa0c4f818e30b6f6737bdd989b7e2b511cae
- https://git.kernel.org/stable/c/e2735b39f044bad7bf2017aef248935525bc0b97
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80593.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80593
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
