# [M] CVE-2017-13694

## Summary
Severity: Medium
Advisory: CVE-2017-13694
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2017-08-25
Source: https://osv.dev/vulnerability/CVE-2017-13694
Type: osv

## Details
The acpi_ps_complete_final_op() function in drivers/acpi/acpica/psobject.c in the Linux kernel through 4.12.9 does not flush the node and node_ext caches and causes a kernel stack dump, which allows local users to obtain sensitive information from kernel memory and bypass the KASLR protection mechanism (in the kernel through 4.9) via a crafted ACPI table.

## References
- http://www.securityfocus.com/bid/100500
- https://github.com/acpica/acpica/pull/278
- https://github.com/acpica/acpica/pull/278/commits/4a0243ecb4c94e2d73510d096c5ea4d0711fc6c0
- https://patchwork.kernel.org/patch/9806085/
