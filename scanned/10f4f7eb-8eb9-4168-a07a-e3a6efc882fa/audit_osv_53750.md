# [M] CVE-2023-23006

## Summary
Severity: Medium
Advisory: CVE-2023-23006
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-03-01
Source: https://osv.dev/vulnerability/CVE-2023-23006
Type: osv

## Details
In the Linux kernel before 5.15.13, drivers/net/ethernet/mellanox/mlx5/core/steering/dr_domain.c misinterprets the mlx5_get_uars_page return value (expects it to be NULL in the error case, whereas it is actually an error pointer).

## References
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.15.13
- https://github.com/torvalds/linux/commit/6b8b42585886c59a008015083282aae434349094
