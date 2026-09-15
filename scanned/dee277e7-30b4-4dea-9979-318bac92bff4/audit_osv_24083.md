# [H] netfilter: nf_tables: possible module reference underflow in error path

## Summary
Severity: High
Advisory: CVE-2022-50048
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-06-18
Source: https://osv.dev/vulnerability/CVE-2022-50048
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.11.0 <5.15.63, >=5.16.0 <5.19.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: nf_tables: possible module reference underflow in error path

dst->ops is set on when nft_expr_clone() fails, but module refcount has
not been bumped yet, therefore nft_expr_destroy() leads to module
reference underflow.

## References
- https://git.kernel.org/stable/c/1e52e6cfec6342c3d0df47dc3a76724fb3dabf56
- https://git.kernel.org/stable/c/b59bee8b05b0e789b5a298cacb09e8aaa3367a29
- https://git.kernel.org/stable/c/c485c35ff6783ccd12c160fcac6a0e504e83e0bf
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50048.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50048
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
