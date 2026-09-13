# [C] ipv6: sr: Fix MAC comparison to be constant-time

## Summary
Severity: Critical
Advisory: CVE-2025-39702
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-05
Source: https://osv.dev/vulnerability/CVE-2025-39702
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.10.0 <5.10.249, >=5.11.0 <5.15.190, >=5.16.0 <6.1.149, >=6.2.0 <6.6.103, >=6.7.0 <6.12.44, >=6.13.0 <6.16.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

ipv6: sr: Fix MAC comparison to be constant-time

To prevent timing attacks, MACs need to be compared in constant time.
Use the appropriate helper function for this.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-032379.html
- https://git.kernel.org/stable/c/3b348c9c8d2ca2c67559ffd0e258ae7e1107d4f0
- https://git.kernel.org/stable/c/3ddd55cf19ed6cc62def5e3af10c2a9df1b861c3
- https://git.kernel.org/stable/c/86b6d34717fe0570afce07ee79b8eeb40341f831
- https://git.kernel.org/stable/c/a458b2902115b26a25d67393b12ddd57d1216aaa
- https://git.kernel.org/stable/c/b3967c493799e63f648e9c7b6cb063aa2aed04e7
- https://git.kernel.org/stable/c/f7878d47560d61e3f370aca3cebb8f42a55b990a
- https://git.kernel.org/stable/c/ff55a452d56490047f5233cc48c5d933f8586884
- https://lists.debian.org/debian-lts-announce/2025/10/msg00008.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39702.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39702
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
