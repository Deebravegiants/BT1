# [H] arp: use RCU protection in arp_xmit()

## Summary
Severity: High
Advisory: CVE-2025-21762
Ecosystem: Linux
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-27
Source: https://osv.dev/vulnerability/CVE-2025-21762
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.4.0 <5.4.291, >=5.5.0 <5.10.235, >=5.11.0 <5.15.179, >=5.16.0 <6.1.129, >=6.2.0 <6.6.79, >=6.7.0 <6.12.16, >=6.13.0 <6.13.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

arp: use RCU protection in arp_xmit()

arp_xmit() can be called without RTNL or RCU protection.

Use RCU protection to avoid potential UAF.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://cert-portal.siemens.com/productcert/html/ssa-503939.html
- https://git.kernel.org/stable/c/01d1b5c9abcaff29a43f1d17a19c33eec92c7dbe
- https://git.kernel.org/stable/c/10f555e3f573d004ae9d89b3276abb58c4ede5c3
- https://git.kernel.org/stable/c/2c331718d3389b6c5f6855078ab7171849e016bd
- https://git.kernel.org/stable/c/307cd1e2d3cb1cbc6c40c679cada6d7168b18431
- https://git.kernel.org/stable/c/a42b69f692165ec39db42d595f4f65a4c8f42e44
- https://git.kernel.org/stable/c/d9366ac2f956a1948b68c0500f84a3462ff2ed8a
- https://git.kernel.org/stable/c/e9f4dee534eb1b225b0a120395ad9bc2afe164d3
- https://git.kernel.org/stable/c/f189654459423d4d48bef2d120b4bfba559e6039
- https://lists.debian.org/debian-lts-announce/2025/03/msg00028.html
- https://lists.debian.org/debian-lts-announce/2025/05/msg00030.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21762.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21762
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
