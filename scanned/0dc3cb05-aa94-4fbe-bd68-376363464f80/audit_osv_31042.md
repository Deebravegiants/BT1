# [H] net/mlx5e: Skip restore TC rules for vport rep without loaded flag

## Summary
Severity: High
Advisory: CVE-2024-57801
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-01-15
Source: https://osv.dev/vulnerability/CVE-2024-57801
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.6.0 <6.6.70, >=6.7.0 <6.12.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/mlx5e: Skip restore TC rules for vport rep without loaded flag

During driver unload, unregister_netdev is called after unloading
vport rep. So, the mlx5e_rep_priv is already freed while trying to get
rpriv->netdev, or walk rpriv->tc_ht, which results in use-after-free.
So add the checking to make sure access the data of vport rep which is
still loaded.

## References
- https://git.kernel.org/stable/c/3e45dd1622a2c1a83c11bf42fdd8c1810123d6c0
- https://git.kernel.org/stable/c/47c78d3fc26e38ab805613a0f592dc8a820c7c64
- https://git.kernel.org/stable/c/5a03b368562a7ff5f5f1f63b5adf8309cbdbd5be
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/57xxx/CVE-2024-57801.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-57801
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
