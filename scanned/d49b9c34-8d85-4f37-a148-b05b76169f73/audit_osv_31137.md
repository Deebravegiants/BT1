# [M] ubifs: skip dumping tnc tree when zroot is null

## Summary
Severity: Medium
Advisory: CVE-2024-58058
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-03-06
Source: https://osv.dev/vulnerability/CVE-2024-58058
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.27 <5.4.291, >=5.5.0 <5.10.235, >=5.11.0 <5.15.179, >=5.16.0 <6.1.129, >=6.2.0 <6.6.76, >=6.7.0 <6.12.13, >=6.13.0 <6.13.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

ubifs: skip dumping tnc tree when zroot is null

Clearing slab cache will free all znode in memory and make
c->zroot.znode = NULL, then dumping tnc tree will access
c->zroot.znode which cause null pointer dereference.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://git.kernel.org/stable/c/1787cd67bb94b106555ffe64f887f6aa24b47010
- https://git.kernel.org/stable/c/2a987950df825d0144370e700dc5fb337684ffba
- https://git.kernel.org/stable/c/40e25a3c0063935763717877bb2a814c081509ff
- https://git.kernel.org/stable/c/428aff8f7cfb0d9a8854477648022cef96bcab28
- https://git.kernel.org/stable/c/6211c11fc20424bbc6d79c835c7c212b553ae898
- https://git.kernel.org/stable/c/77e5266e3d3faa6bdcf20d9c68a8972f6aa06522
- https://git.kernel.org/stable/c/bdb0ca39e0acccf6771db49c3f94ed787d05f2d7
- https://git.kernel.org/stable/c/e01b55f261ccc96e347eba4931e4429d080d879d
- https://lists.debian.org/debian-lts-announce/2025/03/msg00028.html
- https://lists.debian.org/debian-lts-announce/2025/05/msg00030.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/58xxx/CVE-2024-58058.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-58058
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
