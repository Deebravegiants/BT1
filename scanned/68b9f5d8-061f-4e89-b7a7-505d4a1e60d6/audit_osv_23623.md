# [M] ath9k_htc: fix uninit value bugs

## Summary
Severity: Medium
Advisory: CVE-2022-49235
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49235
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.35 <4.9.311, >=4.10.0 <4.14.276, >=4.15.0 <4.19.238, >=4.20.0 <5.4.189, >=5.5.0 <5.10.110, >=5.11.0 <5.15.33, >=5.16.0 <5.16.19, >=5.17.0 <5.17.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

ath9k_htc: fix uninit value bugs

Syzbot reported 2 KMSAN bugs in ath9k. All of them are caused by missing
field initialization.

In htc_connect_service() svc_meta_len and pad are not initialized. Based
on code it looks like in current skb there is no service data, so simply
initialize svc_meta_len to 0.

htc_issue_send() does not initialize htc_frame_hdr::control array. Based
on firmware code, it will initialize it by itself, so simply zero whole
array to make KMSAN happy

Fail logs:

BUG: KMSAN: kernel-usb-infoleak in usb_submit_urb+0x6c1/0x2aa0 drivers/usb/core/urb.c:430
 usb_submit_urb+0x6c1/0x2aa0 drivers/usb/core/urb.c:430
 hif_usb_send_regout drivers/net/wireless/ath/ath9k/hif_usb.c:127 [inline]
 hif_usb_send+0x5f0/0x16f0 drivers/net/wireless/ath/ath9k/hif_usb.c:479
 htc_issue_send drivers/net/wireless/ath/ath9k/htc_hst.c:34 [inline]
 htc_connect_service+0x143e/0x1960 drivers/net/wireless/ath/ath9k/htc_hst.c:275
...

Uninit was created at:
 slab_post_alloc_hook mm/slab.h:524 [inline]
 slab_alloc_node mm/slub.c:3251 [inline]
 __kmalloc_node_track_caller+0xe0c/0x1510 mm/slub.c:4974
 kmalloc_reserve net/core/skbuff.c:354 [inline]
 __alloc_skb+0x545/0xf90 net/core/skbuff.c:426
 alloc_skb include/linux/skbuff.h:1126 [inline]
 htc_connect_service+0x1029/0x1960 drivers/net/wireless/ath/ath9k/htc_hst.c:258
...

Bytes 4-7 of 18 are uninitialized
Memory access of size 18 starts at ffff888027377e00

BUG: KMSAN: kernel-usb-infoleak in usb_submit_urb+0x6c1/0x2aa0 drivers/usb/core/urb.c:430
 usb_submit_urb+0x6c1/0x2aa0 drivers/usb/core/urb.c:430
 hif_usb_send_regout drivers/net/wireless/ath/ath9k/hif_usb.c:127 [inline]
 hif_usb_send+0x5f0/0x16f0 drivers/net/wireless/ath/ath9k/hif_usb.c:479
 htc_issue_send drivers/net/wireless/ath/ath9k/htc_hst.c:34 [inline]
 htc_connect_service+0x143e/0x1960 drivers/net/wireless/ath/ath9k/htc_hst.c:275
...

Uninit was created at:
 slab_post_alloc_hook mm/slab.h:524 [inline]
 slab_alloc_node mm/slub.c:3251 [inline]
 __kmalloc_node_track_caller+0xe0c/0x1510 mm/slub.c:4974
 kmalloc_reserve net/core/skbuff.c:354 [inline]
 __alloc_skb+0x545/0xf90 net/core/skbuff.c:426
 alloc_skb include/linux/skbuff.h:1126 [inline]
 htc_connect_service+0x1029/0x1960 drivers/net/wireless/ath/ath9k/htc_hst.c:258
...

Bytes 16-17 of 18 are uninitialized
Memory access of size 18 starts at ffff888027377e00

## References
- https://git.kernel.org/stable/c/0b700f7d06492de34964b6f414120043364f8191
- https://git.kernel.org/stable/c/11f11ac281f0c0b363d2940204f28bae0422ed71
- https://git.kernel.org/stable/c/4d244b731188e0b63fc40a9d2dec72e9181fb37c
- https://git.kernel.org/stable/c/5abf2b761b998063f5e2bae93fd4ab10e2a80f10
- https://git.kernel.org/stable/c/5c2a6a8daa17a3f65b38b9a5574bb362c13fa1d9
- https://git.kernel.org/stable/c/7da6169b6ebb75816b57be3beb829afa74f3b4b6
- https://git.kernel.org/stable/c/d1e0df1c57bd30871dd1c855742a7c346dbca853
- https://git.kernel.org/stable/c/e352acdd378e9263cc4c6018e588f2dac7161d07
- https://git.kernel.org/stable/c/ee4222052a76559c20e821bc3519cefb58b6d3e9
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49235.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49235
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
