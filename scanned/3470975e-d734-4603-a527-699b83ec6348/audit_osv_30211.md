# [H] net: phy: dp83869: fix memory corruption when enabling fiber

## Summary
Severity: High
Advisory: CVE-2024-50188
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-11-08
Source: https://osv.dev/vulnerability/CVE-2024-50188
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.10.0 <5.10.227, >=5.11.0 <5.15.168, >=5.16.0 <6.1.113, >=6.2.0 <6.6.57, >=6.7.0 <6.11.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: phy: dp83869: fix memory corruption when enabling fiber

When configuring the fiber port, the DP83869 PHY driver incorrectly
calls linkmode_set_bit() with a bit mask (1 << 10) rather than a bit
number (10). This corrupts some other memory location -- in case of
arm64 the priv pointer in the same structure.

Since the advertising flags are updated from supported at the end of the
function the incorrect line isn't needed at all and can be removed.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://cert-portal.siemens.com/productcert/html/ssa-355557.html
- https://git.kernel.org/stable/c/21b5af7f0c99b3bf1fd02016e6708b613acbcaf4
- https://git.kernel.org/stable/c/9ca634676ff66e1d616259e136f96f96b2a1759a
- https://git.kernel.org/stable/c/a842e443ca8184f2dc82ab307b43a8b38defd6a5
- https://git.kernel.org/stable/c/ad0d76b8ee5db063791cc2e7a30ffc9852ac37c4
- https://git.kernel.org/stable/c/c1944b4253649fc6f2fb53e7d6302eb414d2182c
- https://git.kernel.org/stable/c/e3f2de32dae35bc7d173377dc97b5bc9fcd9fc84
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50188.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50188
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
