# [M] eth: mlx4: Fix IS_ERR() vs NULL check bug in mlx4_en_create_rx_ring

## Summary
Severity: Medium
Advisory: CVE-2025-39858
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-19
Source: https://osv.dev/vulnerability/CVE-2025-39858
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.15.0 <6.16.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

eth: mlx4: Fix IS_ERR() vs NULL check bug in mlx4_en_create_rx_ring

Replace NULL check with IS_ERR() check after calling page_pool_create()
since this function returns error pointers (ERR_PTR).
Using NULL check could lead to invalid pointer dereference.

## References
- https://git.kernel.org/stable/c/7b77d8841a98a9f45c8a615222c698df8dec581c
- https://git.kernel.org/stable/c/e580beaf43d563aaf457f1c7f934002355ebfe7b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39858.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39858
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
