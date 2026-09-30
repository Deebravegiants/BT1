# [H] Use-after-free in Linux kernel's ipv4: igmp component

## Summary
Severity: High
Advisory: CVE-2023-6932
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-12-19
Source: https://osv.dev/vulnerability/CVE-2023-6932
Type: osv

## Details
A use-after-free vulnerability in the Linux kernel's ipv4: igmp component can be exploited to achieve local privilege escalation.

A race condition can be exploited to cause a timer be mistakenly registered on a RCU read locked object which is freed by another thread.

We recommend upgrading past commit e2b706c691905fe78468c361aaabc719d0a496f1.

## References
- http://packetstormsecurity.com/files/177029/Kernel-Live-Patch-Security-Notice-LSN-0100-1.html
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://cert-portal.siemens.com/productcert/html/ssa-398330.html
- https://cert-portal.siemens.com/productcert/html/ssa-613116.html
- https://cert-portal.siemens.com/productcert/html/ssa-794697.html
- https://git.kernel.org
- https://kernel.dance/e2b706c691905fe78468c361aaabc719d0a496f1
- https://lists.debian.org/debian-lts-announce/2024/01/msg00004.html
- https://lists.debian.org/debian-lts-announce/2024/01/msg00005.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/6xxx/CVE-2023-6932.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-6932
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit?id=e2b706c691905fe78468c361aaabc719d0a496f1
