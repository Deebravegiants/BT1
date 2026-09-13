# [H] spi: fix use-after-free on controller registration failure

## Summary
Severity: High
Advisory: CVE-2026-31389
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-03
Source: https://osv.dev/vulnerability/CVE-2026-31389
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.0.0 <6.1.167, >=6.2.0 <6.6.130, >=6.7.0 <6.12.78, >=6.13.0 <6.18.20, >=6.19.0 <6.19.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

spi: fix use-after-free on controller registration failure

Make sure to deregister from driver core also in the unlikely event that
per-cpu statistics allocation fails during controller registration to
avoid use-after-free (of driver resources) and unclocked register
accesses.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://git.kernel.org/stable/c/0e23f50086da7d0b183dfeac26021acfcdee086b
- https://git.kernel.org/stable/c/23b51bad2eb8787aa74324cfccefb258515ae5ba
- https://git.kernel.org/stable/c/6bbd385b30c7fb6c7ee0669e9ada91490938c051
- https://git.kernel.org/stable/c/80f3e8cd2b4ad355b2ad2024cf423f6d183404f7
- https://git.kernel.org/stable/c/8634e05b08ead636e926022f4a98416e13440df9
- https://git.kernel.org/stable/c/afe27c1f43aa57530011f419be6ddf71306565d2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31389.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31389
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
