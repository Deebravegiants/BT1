# [M] be2net: fix potential memory leak in be_xmit()

## Summary
Severity: Medium
Advisory: CVE-2024-50167
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-11-07
Source: https://osv.dev/vulnerability/CVE-2024-50167
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.2.0 <4.19.323, >=4.20.0 <5.4.285, >=5.5.0 <5.10.229, >=5.11.0 <5.15.170, >=5.16.0 <6.1.115, >=6.2.0 <6.6.59, >=6.7.0 <6.11.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

be2net: fix potential memory leak in be_xmit()

The be_xmit() returns NETDEV_TX_OK without freeing skb
in case of be_xmit_enqueue() fails, add dev_kfree_skb_any() to fix it.

## References
- https://git.kernel.org/stable/c/4c5f170ef4f85731a4d43ad9a6ac51106c0946be
- https://git.kernel.org/stable/c/641c1beed52bf3c6deb0193fe4d38ec9ff75d2ae
- https://git.kernel.org/stable/c/6b7ce8ee01c33c380aaa5077ff25215492e7eb0e
- https://git.kernel.org/stable/c/77bc881d370e850b7f3cd2b5eae67d596b40efbc
- https://git.kernel.org/stable/c/919ab6e2370289a2748780f44a43333cd3878aa7
- https://git.kernel.org/stable/c/941026023c256939943a47d1c66671526befbb26
- https://git.kernel.org/stable/c/e4dd8bfe0f6a23acd305f9b892c00899089bd621
- https://git.kernel.org/stable/c/e86a79b804e26e3b7f1e415b22a085c0bb7ea3d3
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50167.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50167
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
