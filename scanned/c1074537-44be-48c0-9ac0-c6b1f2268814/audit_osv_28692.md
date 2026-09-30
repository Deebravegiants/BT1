# [H] nfc: nci: Fix uninit-value in nci_dev_up and nci_ntf_packet

## Summary
Severity: High
Advisory: CVE-2024-35915
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-19
Source: https://osv.dev/vulnerability/CVE-2024-35915
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.2.0 <4.19.312, >=4.20.0 <5.4.274, >=5.5.0 <5.10.215, >=5.11.0 <5.15.154, >=5.16.0 <6.1.85, >=6.2.0 <6.6.26, >=6.7.0 <6.8.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

nfc: nci: Fix uninit-value in nci_dev_up and nci_ntf_packet

syzbot reported the following uninit-value access issue [1][2]:

nci_rx_work() parses and processes received packet. When the payload
length is zero, each message type handler reads uninitialized payload
and KMSAN detects this issue. The receipt of a packet with a zero-size
payload is considered unexpected, and therefore, such packets should be
silently discarded.

This patch resolved this issue by checking payload size before calling
each message type handler codes.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://git.kernel.org/stable/c/03fe259649a551d336a7f20919b641ea100e3fff
- https://git.kernel.org/stable/c/11387b2effbb55f58dc2111ef4b4b896f2756240
- https://git.kernel.org/stable/c/755e53bbc61bc1aff90eafa64c8c2464fd3dfa3c
- https://git.kernel.org/stable/c/8948e30de81faee87eeee01ef42a1f6008f5a83a
- https://git.kernel.org/stable/c/a946ebee45b09294c8b0b0e77410b763c4d2817a
- https://git.kernel.org/stable/c/ac68d9fa09e410fa3ed20fb721d56aa558695e16
- https://git.kernel.org/stable/c/b51ec7fc9f877ef869c01d3ea6f18f6a64e831a7
- https://git.kernel.org/stable/c/d24b03535e5eb82e025219c2f632b485409c898f
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://lists.debian.org/debian-lts-announce/2024/06/msg00020.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/35xxx/CVE-2024-35915.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-35915
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
