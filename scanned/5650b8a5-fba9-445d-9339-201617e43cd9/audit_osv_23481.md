# [H] net/mlx5: DR, Fix slab-out-of-bounds in mlx5_cmd_dr_create_fte

## Summary
Severity: High
Advisory: CVE-2022-48932
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-08-22
Source: https://osv.dev/vulnerability/CVE-2022-48932
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.16.0 <5.16.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/mlx5: DR, Fix slab-out-of-bounds in mlx5_cmd_dr_create_fte

When adding a rule with 32 destinations, we hit the following out-of-band
access issue:

  BUG: KASAN: slab-out-of-bounds in mlx5_cmd_dr_create_fte+0x18ee/0x1e70

This patch fixes the issue by both increasing the allocated buffers to
accommodate for the needed actions and by checking the number of actions
to prevent this issue when a rule with too many actions is provided.

## References
- https://git.kernel.org/stable/c/0aec12d97b2036af0946e3d582144739860ac07b
- https://git.kernel.org/stable/c/4ad319cdfbe555b4ff67bc608736c46a6930c848
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/48xxx/CVE-2022-48932.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-48932
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
