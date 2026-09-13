# [H] netfilter: ebtables: module names must be null-terminated

## Summary
Severity: High
Advisory: CVE-2026-64412
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-07-25
Source: https://osv.dev/vulnerability/CVE-2026-64412
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.6.0 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.96, >=6.13.0 <6.18.39, >=6.19.0 <7.1.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: ebtables: module names must be null-terminated

We need to explicitly check the length, else we may pass non-null
terminated string to request_module().

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://git.kernel.org/stable/c/084d23f818321390509e9738a0b08bbf46df6425
- https://git.kernel.org/stable/c/0ddca0f90fa3395111d078ae4399615cf3ea94aa
- https://git.kernel.org/stable/c/13a5f532e3a4fc75c33060a026def1572c208643
- https://git.kernel.org/stable/c/43dd2332b8a27b3ac5108791680cade654ab0f96
- https://git.kernel.org/stable/c/5777c8f1c3610786d8482b8f620f40fccaf1542b
- https://git.kernel.org/stable/c/7b217960e88b5d2d1e8cdcbcaf3bdf6fe199a0c8
- https://git.kernel.org/stable/c/d2367d99f2455f373996d9ddbe833dbe9f942213
- https://git.kernel.org/stable/c/da32e78bbb187ed7b137e0007034185570a3a172
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64412.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64412
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
