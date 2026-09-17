# [H] IB/mlx5: Fix transport-domain rollback and initialize lb mutex earlier

## Summary
Severity: High
Advisory: CVE-2026-74397
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74397
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.5.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

IB/mlx5: Fix transport-domain rollback and initialize lb mutex earlier

mlx5_ib_alloc_transport_domain() allocates a transport domain and then
may fail in mlx5_ib_enable_lb(). In that case, the allocated TD is leaked.

Fix this by deallocating the TD when mlx5_ib_enable_lb() returns an
error. Also return 0 explicitly in the no-loopback-capability success
branch, and move dev->lb.mutex initialization to mlx5_ib_stage_init_init().

## References
- https://git.kernel.org/stable/c/2c3b2667dad69d56774b79db763acb3a1bee0fc0
- https://git.kernel.org/stable/c/37fc3cc0f924fd8d0f0cf87b92672dec75a32e57
- https://git.kernel.org/stable/c/65e344925fa30abf50c8de8c150b397715fa2066
- https://git.kernel.org/stable/c/e79389115b9d27287ff6230a9750675106ed7668
- https://git.kernel.org/stable/c/f88e12c95fc19f719e06ca1e9eb20fdad68ef61a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74397.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74397
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
