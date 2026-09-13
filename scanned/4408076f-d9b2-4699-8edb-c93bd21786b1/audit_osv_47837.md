# [M] CVE-2017-13695

## Summary
Severity: Medium
Advisory: CVE-2017-13695
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2017-08-25
Source: https://osv.dev/vulnerability/CVE-2017-13695
Type: osv

## Details
The acpi_ns_evaluate() function in drivers/acpi/acpica/nseval.c in the Linux kernel through 4.12.9 does not flush the operand cache and causes a kernel stack dump, which allows local users to obtain sensitive information from kernel memory and bypass the KASLR protection mechanism (in the kernel through 4.9) via a crafted ACPI table.

## References
- https://usn.ubuntu.com/3762-1/
- https://usn.ubuntu.com/3762-2/
- https://usn.ubuntu.com/3696-1/
- https://usn.ubuntu.com/3696-2/
- http://www.securityfocus.com/bid/100497
- https://github.com/acpica/acpica/pull/296/commits/37f2c716f2c6ab14c3ba557a539c3ee3224931b5
- https://patchwork.kernel.org/patch/9850567/
