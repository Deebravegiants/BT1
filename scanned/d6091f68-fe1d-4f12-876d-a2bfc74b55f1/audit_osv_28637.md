# [H] mmc: core: Avoid negative index with array access

## Summary
Severity: High
Advisory: CVE-2024-35813
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-17
Source: https://osv.dev/vulnerability/CVE-2024-35813
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.4.274, >=5.5.0 <5.10.215, >=5.11.0 <5.15.154, >=5.16.0 <6.1.84, >=6.2.0 <6.6.24, >=6.7.0 <6.7.12, >=6.8.0 <6.8.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

mmc: core: Avoid negative index with array access

Commit 4d0c8d0aef63 ("mmc: core: Use mrq.sbc in close-ended ffu") assigns
prev_idata = idatas[i - 1], but doesn't check that the iterator i is
greater than zero. Let's fix this by adding a check.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://git.kernel.org/stable/c/064db53f9023a2d5877a2d12de6bc27995f6ca56
- https://git.kernel.org/stable/c/2b539c88940e22494da80a93ee1c5a28bbad10f6
- https://git.kernel.org/stable/c/4466677dcabe2d70de6aa3d4bd4a4fafa94a71f2
- https://git.kernel.org/stable/c/7d0e8a6147550aa058fa6ade8583ad252aa61304
- https://git.kernel.org/stable/c/81b8645feca08a54c7c4bf36e7b176f4983b2f28
- https://git.kernel.org/stable/c/ad9cc5e9e53ab94aa0c7ac65d43be7eb208dcb55
- https://git.kernel.org/stable/c/b9a7339ae403035ffe7fc37cb034b36947910f68
- https://git.kernel.org/stable/c/cf55a7acd1ed38afe43bba1c8a0935b51d1dc014
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/35xxx/CVE-2024-35813.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-35813
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
