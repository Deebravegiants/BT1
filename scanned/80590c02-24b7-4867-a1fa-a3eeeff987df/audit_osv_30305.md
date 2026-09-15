# [M] HID: core: zero-initialize the report buffer

## Summary
Severity: Medium
Advisory: CVE-2024-50302
Aliases: A-380395346, ASB-A-380395346
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-11-19
Source: https://osv.dev/vulnerability/CVE-2024-50302
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.12.0 <4.19.324, >=4.20.0 <5.4.286, >=5.5.0 <5.10.230, >=5.11.0 <5.15.172, >=5.16.0 <6.1.117, >=6.2.0 <6.6.61, >=6.7.0 <6.11.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

HID: core: zero-initialize the report buffer

Since the report buffer is used by all kinds of drivers in various ways, let's
zero-initialize it during allocation to make sure that it can't be ever used
to leak kernel memory via specially-crafted report.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://cert-portal.siemens.com/productcert/html/ssa-355557.html
- https://git.kernel.org/stable/c/05ade5d4337867929e7ef664e7ac8e0c734f1aaf
- https://git.kernel.org/stable/c/177f25d1292c7e16e1199b39c85480f7f8815552
- https://git.kernel.org/stable/c/1884ab3d22536a5c14b17c78c2ce76d1734e8b0b
- https://git.kernel.org/stable/c/3f9e88f2672c4635960570ee9741778d4135ecf5
- https://git.kernel.org/stable/c/492015e6249fbcd42138b49de3c588d826dd9648
- https://git.kernel.org/stable/c/9d9f5c75c0c7f31766ec27d90f7a6ac673193191
- https://git.kernel.org/stable/c/d7dc68d82ab3fcfc3f65322465da3d7031d4ab46
- https://git.kernel.org/stable/c/e7ea60184e1e88a3c9e437b3265cbb6439aa7e26
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2024-50302
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50302.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50302
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
