# [H] crypto: authencesn - Do not place hiseq at end of dst for out-of-place decryption

## Summary
Severity: High
Advisory: CVE-2026-43033
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-01
Source: https://osv.dev/vulnerability/CVE-2026-43033
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.3.0 <5.10.254, >=5.11.0 <5.15.204, >=5.16.0 <6.1.170, >=6.2.0 <6.6.137, >=6.7.0 <6.12.85, >=6.13.0 <6.18.22, >=6.19.0 <6.19.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

crypto: authencesn - Do not place hiseq at end of dst for out-of-place decryption

When decrypting data that is not in-place (src != dst), there is
no need to save the high-order sequence bits in dst as it could
simply be re-copied from the source.

However, the data to be hashed need to be rearranged accordingly.


Thanks,

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://git.kernel.org/stable/c/153d5520c3f9fd62e71c7e7f9e34b59cf411e555
- https://git.kernel.org/stable/c/5466e7d0cd9e4f9cef9d8f18f18b60e7bc1c77e5
- https://git.kernel.org/stable/c/89fe118b6470119b20c04afc36e45b81a69ea11f
- https://git.kernel.org/stable/c/8c62f618576519dbed6816fafc623ce592953025
- https://git.kernel.org/stable/c/cded4002d22177e8deaca1f257ecd932c9582b6b
- https://git.kernel.org/stable/c/d0c4ff6812386880f30bc64c2921299cc4d7b47f
- https://git.kernel.org/stable/c/d589abd8b019b07075fda255ceab8c8e950cdb3f
- https://git.kernel.org/stable/c/e02494114ebf7c8b42777c6cd6982f113bfdbec7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43033.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43033
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
