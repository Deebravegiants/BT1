# [H] wifi: mwifiex: Fix OOB and integer underflow when rx packets

## Summary
Severity: High
Advisory: CVE-2023-53226
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-15
Source: https://osv.dev/vulnerability/CVE-2023-53226
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.7.0 <4.14.326, >=4.15.0 <4.19.295, >=4.20.0 <5.4.257, >=5.5.0 <5.10.195, >=5.11.0 <5.15.132, >=5.16.0 <6.1.53, >=6.2.0 <6.4.16, >=6.5.0 <6.5.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: mwifiex: Fix OOB and integer underflow when rx packets

Make sure mwifiex_process_mgmt_packet,
mwifiex_process_sta_rx_packet and mwifiex_process_uap_rx_packet,
mwifiex_uap_queue_bridged_pkt and mwifiex_process_rx_packet
not out-of-bounds access the skb->data buffer.

## References
- https://git.kernel.org/stable/c/11958528161731c58e105b501ed60b83a91ea941
- https://git.kernel.org/stable/c/29eca8b7863d1d7de6c5b746b374e3487d14f154
- https://git.kernel.org/stable/c/3975e21d4d01efaf0296ded40d11c06589c49245
- https://git.kernel.org/stable/c/3fe3923d092e22d87d1ed03e2729db444b8c1331
- https://git.kernel.org/stable/c/650d1bc02fba7b42f476d8b6643324abac5921ed
- https://git.kernel.org/stable/c/7c54b6fc39eb1aac51cf2945f8a25e2a47fdca02
- https://git.kernel.org/stable/c/8824aa4ab62c800f75d96f48e1883a5f56ec5869
- https://git.kernel.org/stable/c/a7300e3800e9fd5405e88ce67709c1a97783b9c8
- https://git.kernel.org/stable/c/f517c97fc129995de77dd06aa5a74f909ebf568f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53226.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53226
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
