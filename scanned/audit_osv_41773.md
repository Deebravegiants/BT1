# [H] wifi: mt76: add wcid publish check in mt76_sta_add

## Summary
Severity: High
Advisory: CVE-2026-63832
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-63832
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.14.0 <6.18.38, >=6.19.0 <7.1.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: mt76: add wcid publish check in mt76_sta_add

Since mt7925_mac_sta_add publishes wcid, add publish check in mt76_sta_add
to avoid reinitializing the wcid->poll_list.

Found dev->sta_poll_list corruption when using mt7925 and 7.1-rc4.
According to the corruption information, prev->next was changed to itself.

wlan0: disconnect from AP 90:fb:5d:94:8b:e3 for new auth to 90:fb:5d:94:8b:e2
wlan0: authenticate with 90:fb:5d:94:8b:e2 (local address=84:9e:56:9c:7e:6b)
wlan0: send auth to 90:fb:5d:94:8b:e2 (try 1/3)
 slab kmalloc-8k start ffff8c80958a6000 pointer offset 4160 size 8192
list_add corruption. prev->next should be next (ffff8c808a7488f8), but was ffff8c80958a7040. (prev=ffff8c80958a7040).

 mt76_wcid_add_poll+0x95/0xd0 [mt76]
 mt7925_mac_add_txs.part.0+0xa5/0xe0 [mt7925_common]
 mt7925_rx_check+0xa7/0xc0 [mt7925_common]
 mt76_dma_rx_poll+0x50d/0x790 [mt76]
 mt792x_poll_rx+0x52/0xe0 [mt792x_lib]

## References
- https://git.kernel.org/stable/c/20b126920a259df4d7dcae19fcfe2c57a74d6b2e
- https://git.kernel.org/stable/c/3c499851753a24d2e148d4e9ca51764c0c51554e
- https://git.kernel.org/stable/c/55e014aaec650ede08b693ba59c8d0443f13f11c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63832.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-63832
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
