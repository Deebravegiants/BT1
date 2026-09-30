# [H] octeontx2-pf: Fix potential use after free in otx2_tc_add_flow()

## Summary
Severity: High
Advisory: CVE-2025-39978
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-15
Source: https://osv.dev/vulnerability/CVE-2025-39978
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.14.0 <6.1.155, >=6.2.0 <6.6.109, >=6.7.0 <6.12.50, >=6.13.0 <6.16.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

octeontx2-pf: Fix potential use after free in otx2_tc_add_flow()

This code calls kfree_rcu(new_node, rcu) and then dereferences "new_node"
and then dereferences it on the next line.  Two lines later, we take
a mutex so I don't think this is an RCU safe region.  Re-order it to do
the dereferences before queuing up the free.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://git.kernel.org/stable/c/5723120423a753a220b8b2954b273838b9d7e74a
- https://git.kernel.org/stable/c/a8a63f27c3a8a3714210d32b12fd0f16d0337414
- https://git.kernel.org/stable/c/c41b2941a024d4ec7c768e16ffb10a74b188fced
- https://git.kernel.org/stable/c/d9c70e93ec5988ab07ad2a92d9f9d12867f02c56
- https://git.kernel.org/stable/c/df2c071061ed52d2225d97b212d27ecedf456b8a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39978.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39978
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
