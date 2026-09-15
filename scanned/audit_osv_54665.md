# [M] CVE-2024-25740

## Summary
Severity: Medium
Advisory: CVE-2024-25740
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-02-12
Source: https://osv.dev/vulnerability/CVE-2024-25740
Type: osv

## Details
A memory leak flaw was found in the UBI driver in drivers/mtd/ubi/attach.c in the Linux kernel through 6.7.4 for UBI_IOCATT, because kobj->name is not released.

## References
- https://lore.kernel.org/lkml/0171b6cc-95ee-3538-913b-65a391a446b3%40huawei.com/T/
