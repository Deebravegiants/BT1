# [M] platform/x86: int3472: Check for adev == NULL

## Summary
Severity: Medium
Advisory: CVE-2024-58011
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-27
Source: https://osv.dev/vulnerability/CVE-2024-58011
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.14.0 <5.15.195, >=5.16.0 <6.1.129, >=6.2.0 <6.6.78, >=6.7.0 <6.12.14, >=6.13.0 <6.13.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

platform/x86: int3472: Check for adev == NULL

Not all devices have an ACPI companion fwnode, so adev might be NULL. This
can e.g. (theoretically) happen when a user manually binds one of
the int3472 drivers to another i2c/platform device through sysfs.

Add a check for adev not being set and return -ENODEV in that case to
avoid a possible NULL pointer deref in skl_int3472_get_acpi_buffer().

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://git.kernel.org/stable/c/0a30353beca2693d30bde477024d755ffecea514
- https://git.kernel.org/stable/c/46263a0b687a044e645387a9c7692ccd693f09f1
- https://git.kernel.org/stable/c/4f8b210823cc2d1f9d967f089a6c00d025bb237f
- https://git.kernel.org/stable/c/a808ecf878ad646ebc9c83d9fc4ce72fd9c49d3d
- https://git.kernel.org/stable/c/cd2fd6eab480dfc247b737cf7a3d6b009c4d0f1c
- https://git.kernel.org/stable/c/f9c7cc44758f4930b41285a6d54afa8cbd9762b4
- https://lists.debian.org/debian-lts-announce/2025/03/msg00028.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/58xxx/CVE-2024-58011.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-58011
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
