# [H] nfc: nci: Fix uninit-value in nci_rx_work

## Summary
Severity: High
Advisory: CVE-2024-38381
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-06-21
Source: https://osv.dev/vulnerability/CVE-2024-38381
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <4.19.316, >=4.20.0 <5.4.278, >=5.5.0 <5.10.219, >=5.11.0 <5.15.161, >=5.16.0 <6.1.93, >=6.2.0 <6.6.33, >=6.7.0 <6.9.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

nfc: nci: Fix uninit-value in nci_rx_work

syzbot reported the following uninit-value access issue [1]

nci_rx_work() parses received packet from ndev->rx_q. It should be
validated header size, payload size and total packet size before
processing the packet. If an invalid packet is detected, it should be
silently discarded.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://cert-portal.siemens.com/productcert/html/ssa-613116.html
- https://git.kernel.org/stable/c/017ff397624930fd7ac7f1761f3c9d6a7100f68c
- https://git.kernel.org/stable/c/406cfac9debd4a6d3dc5d9258ee086372a8c08b6
- https://git.kernel.org/stable/c/485ded868ed62ceb2acb3a459d7843fd71472619
- https://git.kernel.org/stable/c/ad4d196d2008c7f413167f0a693feb4f0439d7fe
- https://git.kernel.org/stable/c/e4a87abf588536d1cdfb128595e6e680af5cf3ed
- https://git.kernel.org/stable/c/e53a7f8afcbd2886f2a94c5d56757328109730ea
- https://git.kernel.org/stable/c/e8c8e0d0d214c877fbad555df5b3ed558cd9b0c3
- https://git.kernel.org/stable/c/f80b786ab0550d0020191a59077b2c7e069db2d1
- https://lists.debian.org/debian-lts-announce/2024/06/msg00020.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/38xxx/CVE-2024-38381.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-38381
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
