# [H] wifi: rtw88: fix OOB read from firmware RX descriptor exceeding DMA buffer

## Summary
Severity: High
Advisory: CVE-2026-74410
Ecosystem: Linux
CVSS: 8.1 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74410
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.2.0 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: rtw88: fix OOB read from firmware RX descriptor exceeding DMA buffer

In rtw_pci_rx_napi(), new_len is computed as the sum of pkt_len (14-bit
descriptor field, max 16383) and pkt_offset (drv_info_sz + shift, both
firmware-controlled). The result can exceed RTK_PCI_RX_BUF_SIZE (11478),
causing an out-of-bounds read from the pre-allocated DMA buffer when
skb_put_data copies new_len bytes. The USB transport already validates
this (rtw_usb_rx_data_put checks against RTW_USB_MAX_RECVBUF_SZ); the
PCIe path does not.

Add a check that new_len does not exceed the DMA buffer size.

## References
- https://git.kernel.org/stable/c/01155ded5d4dad61840a9a3c33ab56778ef1f100
- https://git.kernel.org/stable/c/08193e733e5d4790e6c937af86d78793b02709be
- https://git.kernel.org/stable/c/1554fa522f16ec7c5c342ad33fe734eeb6eb2452
- https://git.kernel.org/stable/c/26c183a86ea4dd1f2ff90c6f783649e7f5722a10
- https://git.kernel.org/stable/c/45abc14ab3f15da7d689f1a8809c1a01240a94d9
- https://git.kernel.org/stable/c/6a3c384393d3f0b41669ed5a2e88744aad9d87c8
- https://git.kernel.org/stable/c/6e76e9ed273dfb4b3333a5ebbb94958cc5752ab6
- https://git.kernel.org/stable/c/913bd7d3d3d842b5c1d2b908a0201efa8fc79793
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74410.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74410
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
