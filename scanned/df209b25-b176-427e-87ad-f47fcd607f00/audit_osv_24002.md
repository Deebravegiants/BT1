# [M] net: wwan: iosm: fix memory leak in ipc_pcie_read_bios_cfg

## Summary
Severity: Medium
Advisory: CVE-2022-49855
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-05-01
Source: https://osv.dev/vulnerability/CVE-2022-49855
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.14.0 <5.15.79, >=5.16.0 <6.0.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: wwan: iosm: fix memory leak in ipc_pcie_read_bios_cfg

ipc_pcie_read_bios_cfg() is using the acpi_evaluate_dsm() to
obtain the wwan power state configuration from BIOS but is
not freeing the acpi_object. The acpi_evaluate_dsm() returned
acpi_object to be freed.

Free the acpi_object after use.

## References
- https://git.kernel.org/stable/c/13b1ea861e8aeb701bcfbfe436b943efa2d44029
- https://git.kernel.org/stable/c/7560ceef4d2832a67e8781d924e129c7f542376f
- https://git.kernel.org/stable/c/d38a648d2d6cc7bee11c6f533ff9426a00c2a74c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49855.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49855
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
