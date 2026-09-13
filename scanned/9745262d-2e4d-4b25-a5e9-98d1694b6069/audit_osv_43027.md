# [H] net/mlx5: LAG, Fix off-by-one in single-FDB error rollback

## Summary
Severity: High
Advisory: CVE-2026-72345
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72345
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.14.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/mlx5: LAG, Fix off-by-one in single-FDB error rollback

On failure at index i, the reverse cleanup loop in
mlx5_lag_create_single_fdb() starts from i, so the failed index
itself is rolled back. That can operate on uninitialized state or
double-tear-down a rule the add_one path already self-rolled-back.

Start the rollback from i - 1 so only successfully-installed entries
are undone.

## References
- https://git.kernel.org/stable/c/0f0e4ae6975c773f7854fc48932a267f6c79088f
- https://git.kernel.org/stable/c/40cc06bf71476932e5d139fa326dcd0372766e16
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72345.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72345
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
