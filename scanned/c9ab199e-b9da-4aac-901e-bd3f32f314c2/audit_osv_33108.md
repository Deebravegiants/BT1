# [H] s390/sclp: Fix SCCB present check

## Summary
Severity: High
Advisory: CVE-2025-39694
Ecosystem: Linux
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:H)
Published: 2025-09-05
Source: https://osv.dev/vulnerability/CVE-2025-39694
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.16.0 <6.1.149, >=6.2.0 <6.6.103, >=6.7.0 <6.12.44, >=6.13.0 <6.16.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

s390/sclp: Fix SCCB present check

Tracing code called by the SCLP interrupt handler contains early exits
if the SCCB address associated with an interrupt is NULL. This check is
performed after physical to virtual address translation.

If the kernel identity mapping does not start at address zero, the
resulting virtual address is never zero, so that the NULL checks won't
work. Subsequently this may result in incorrect accesses to the first
page of the identity mapping.

Fix this by introducing a function that handles the NULL case before
address translation.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-032379.html
- https://git.kernel.org/stable/c/430fa71027b6ac9bb0ce5532b8d0676777d4219a
- https://git.kernel.org/stable/c/61605c847599fbfdfafe638607841c7d73719081
- https://git.kernel.org/stable/c/86c2825791c3836a8f77a954b9c5ebe6fab410c5
- https://git.kernel.org/stable/c/aa5073ac1a2a274812f3b04c278992e68ff67cc7
- https://git.kernel.org/stable/c/bf83ae3537359af088d6577812ed93113dfbcb7b
- https://lists.debian.org/debian-lts-announce/2025/10/msg00008.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39694.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39694
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
