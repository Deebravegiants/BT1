# [M] CVE-2017-13693

## Summary
Severity: Medium
Advisory: CVE-2017-13693
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2017-08-25
Source: https://osv.dev/vulnerability/CVE-2017-13693
Type: osv

## Details
The acpi_ds_create_operands() function in drivers/acpi/acpica/dsutils.c in the Linux kernel through 4.12.9 does not flush the operand cache and causes a kernel stack dump, which allows local users to obtain sensitive information from kernel memory and bypass the KASLR protection mechanism (in the kernel through 4.9) via a crafted ACPI table.

## References
- http://www.securityfocus.com/bid/100502
- https://github.com/acpica/acpica/pull/295
- https://github.com/acpica/acpica/pull/295/commits/987a3b5cf7175916e2a4b6ea5b8e70f830dfe732
- https://patchwork.kernel.org/patch/9919053/
