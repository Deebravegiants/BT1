# [M] vt: fix unicode buffer corruption when deleting characters

## Summary
Severity: Medium
Advisory: CVE-2024-35823
Ecosystem: Linux
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2024-05-17
Source: https://osv.dev/vulnerability/CVE-2024-35823
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.7.0 <4.19.312, >=4.20.0 <5.4.274, >=5.5.0 <5.10.215, >=5.11.0 <5.15.154, >=5.16.0 <6.1.84, >=6.2.0 <6.6.24, >=6.7.0 <6.7.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

vt: fix unicode buffer corruption when deleting characters

This is the same issue that was fixed for the VGA text buffer in commit
39cdb68c64d8 ("vt: fix memory overlapping when deleting chars in the
buffer"). The cure is also the same i.e. replace memcpy() with memmove()
due to the overlaping buffers.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://git.kernel.org/stable/c/0190d19d7651c08abc187dac3819c61b726e7e3f
- https://git.kernel.org/stable/c/1581dafaf0d34bc9c428a794a22110d7046d186d
- https://git.kernel.org/stable/c/1ce408f75ccf1e25b3fddef75cca878b55f2ac90
- https://git.kernel.org/stable/c/2933b1e4757a0a5c689cf48d80b1a2a85f237ff1
- https://git.kernel.org/stable/c/7529cbd8b5f6697b369803fe1533612c039cabda
- https://git.kernel.org/stable/c/994a1e583c0c206c8ca7d03334a65b79f4d8bc51
- https://git.kernel.org/stable/c/fc7dfe3d123f00e720be80b920da287810a1f37d
- https://git.kernel.org/stable/c/ff7342090c1e8c5a37015c89822a68b275b46f8a
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://lists.debian.org/debian-lts-announce/2024/06/msg00020.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/35xxx/CVE-2024-35823.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-35823
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
