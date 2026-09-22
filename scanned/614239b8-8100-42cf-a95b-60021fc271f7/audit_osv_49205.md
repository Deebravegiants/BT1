# [M] CVE-2018-5750

## Summary
Severity: Medium
Advisory: CVE-2018-5750
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2018-01-26
Source: https://osv.dev/vulnerability/CVE-2018-5750
Type: osv

## Details
The acpi_smbus_hc_add function in drivers/acpi/sbshc.c in the Linux kernel through 4.14.15 allows local users to obtain sensitive address information by reading dmesg data from an SBS HC printk call.

## References
- https://www.debian.org/security/2018/dsa-4187
- http://www.securitytracker.com/id/1040319
- https://access.redhat.com/errata/RHSA-2018:0676
- https://access.redhat.com/errata/RHSA-2018:1062
- https://access.redhat.com/errata/RHSA-2018:2948
- https://lists.debian.org/debian-lts-announce/2018/05/msg00000.html
- https://usn.ubuntu.com/3698-1/
- https://www.debian.org/security/2018/dsa-4120
- https://usn.ubuntu.com/3631-1/
- https://usn.ubuntu.com/3631-2/
- https://usn.ubuntu.com/3697-1/
- https://usn.ubuntu.com/3697-2/
- https://usn.ubuntu.com/3698-2/
- https://patchwork.kernel.org/patch/10174835/
