# [H] ipv4: use RCU protection in __ip_rt_update_pmtu()

## Summary
Severity: High
Advisory: CVE-2025-21766
Ecosystem: Linux
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-27
Source: https://osv.dev/vulnerability/CVE-2025-21766
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.9.0 <5.15.179, >=5.16.0 <6.1.129, >=6.2.0 <6.6.79, >=6.7.0 <6.12.16, >=6.13.0 <6.13.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

ipv4: use RCU protection in __ip_rt_update_pmtu()

__ip_rt_update_pmtu() must use RCU protection to make
sure the net structure it reads does not disappear.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://git.kernel.org/stable/c/139512191bd06f1b496117c76372b2ce372c9a41
- https://git.kernel.org/stable/c/4583748b65dee4d61bd50a2214715b4237bc152a
- https://git.kernel.org/stable/c/9b1766d1ff5fe496aabe9fc5f4e34e53f35c11c4
- https://git.kernel.org/stable/c/a39f61d212d822b3062d7f70fa0588e50e55664e
- https://git.kernel.org/stable/c/ce3c6165fce0f06305c806696882a3ad4b90e33f
- https://git.kernel.org/stable/c/ea07480b23225942208f1b754fea1e7ec486d37e
- https://lists.debian.org/debian-lts-announce/2025/03/msg00028.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21766.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21766
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
