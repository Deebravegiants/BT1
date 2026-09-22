# [M] CVE-2023-23002

## Summary
Severity: Medium
Advisory: CVE-2023-23002
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-03-01
Source: https://osv.dev/vulnerability/CVE-2023-23002
Type: osv

## Details
In the Linux kernel before 5.16.3, drivers/bluetooth/hci_qca.c misinterprets the devm_gpiod_get_index_optional return value (expects it to be NULL in the error case, whereas it is actually an error pointer).

## References
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.16.3
- https://github.com/torvalds/linux/commit/6845667146a28c09b5dfc401c1ad112374087944
