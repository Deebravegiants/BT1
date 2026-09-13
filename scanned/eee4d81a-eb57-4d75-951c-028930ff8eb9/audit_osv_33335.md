# [H] ipv6: use RCU in ip6_xmit()

## Summary
Severity: High
Advisory: CVE-2025-40135
Ecosystem: Linux
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-11-12
Source: https://osv.dev/vulnerability/CVE-2025-40135
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.13.0 <6.1.167, >=6.2.0 <6.6.130, >=6.7.0 <6.12.78, >=6.13.0 <6.17.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

ipv6: use RCU in ip6_xmit()

Use RCU in ip6_xmit() in order to use dst_dev_rcu() to prevent
possible UAF.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://git.kernel.org/stable/c/9085e56501d93af9f2d7bd16f7fcfacdde47b99c
- https://git.kernel.org/stable/c/bd0905e2122e3680968cd0741966983490bf2ed3
- https://git.kernel.org/stable/c/f0a54d00d2f36de40266f47c27989853e8588656
- https://git.kernel.org/stable/c/f69fec6287565fdeb61f65e700a1184352306943
- https://git.kernel.org/stable/c/f7f9e924f23684b4b23cd9f976cceab24a968e34
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40135.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-40135
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
