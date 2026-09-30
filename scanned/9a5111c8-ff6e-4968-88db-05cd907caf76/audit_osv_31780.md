# [H] ipv6: use RCU protection in ip6_default_advmss()

## Summary
Severity: High
Advisory: CVE-2025-21765
Ecosystem: Linux
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-27
Source: https://osv.dev/vulnerability/CVE-2025-21765
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.26 <5.4.291, >=5.5.0 <5.10.235, >=5.11.0 <5.15.179, >=5.16.0 <6.1.129, >=6.2.0 <6.6.79, >=6.7.0 <6.12.16, >=6.13.0 <6.13.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

ipv6: use RCU protection in ip6_default_advmss()

ip6_default_advmss() needs rcu protection to make
sure the net structure it reads does not disappear.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://git.kernel.org/stable/c/28de355b63ad42309ed5a03ee7c436c90512265b
- https://git.kernel.org/stable/c/3c8ffcd248da34fc41e52a46e51505900115fc2a
- https://git.kernel.org/stable/c/4176a68b0db8fc74ac14fcd00ba8231371051dc2
- https://git.kernel.org/stable/c/550ed693f47370502a71b85382e7f9e6417300b8
- https://git.kernel.org/stable/c/713a40c892f40300d63691d9f85b2a23b48fe1e8
- https://git.kernel.org/stable/c/78ad057472d8c76e0602402269222f9f9c698790
- https://git.kernel.org/stable/c/84212387caadb211cd9dadd6fd5563bd37dc1f5e
- https://git.kernel.org/stable/c/d02f30d220ef9511568a48dba8a9004c65f8d904
- https://lists.debian.org/debian-lts-announce/2025/03/msg00028.html
- https://lists.debian.org/debian-lts-announce/2025/05/msg00030.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21765.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21765
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
