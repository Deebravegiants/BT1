# [M] rtl818x: Prevent using not initialized queues

## Summary
Severity: Medium
Advisory: CVE-2022-49326
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49326
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.15.0 <4.9.318, >=4.10.0 <4.14.283, >=4.15.0 <4.19.247, >=4.20.0 <5.4.198, >=5.5.0 <5.10.121, >=5.11.0 <5.15.46, >=5.16.0 <5.17.14, >=5.18.0 <5.18.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

rtl818x: Prevent using not initialized queues

Using not existing queues can panic the kernel with rtl8180/rtl8185 cards.
Ignore the skb priority for those cards, they only have one tx queue. Pierre
Asselin (pa@panix.com) reported the kernel crash in the Gentoo forum:

https://forums.gentoo.org/viewtopic-t-1147832-postdays-0-postorder-asc-start-25.html

He also confirmed that this patch fixes the issue. In summary this happened:

After updating wpa_supplicant from 2.9 to 2.10 the kernel crashed with a
"divide error: 0000" when connecting to an AP. Control port tx now tries to
use IEEE80211_AC_VO for the priority, which wpa_supplicants starts to use in
2.10.

Since only the rtl8187se part of the driver supports QoS, the priority
of the skb is set to IEEE80211_AC_BE (2) by mac80211 for rtl8180/rtl8185
cards.

rtl8180 is then unconditionally reading out the priority and finally crashes on
drivers/net/wireless/realtek/rtl818x/rtl8180/dev.c line 544 without this
patch:
	idx = (ring->idx + skb_queue_len(&ring->queue)) % ring->entries

"ring->entries" is zero for rtl8180/rtl8185 cards, tx_ring[2] never got
initialized.

## References
- https://git.kernel.org/stable/c/6ad81ad0cf5744738ce94c8e64051ddd80a1734c
- https://git.kernel.org/stable/c/746285cf81dc19502ab238249d75f5990bd2d231
- https://git.kernel.org/stable/c/769ec2a824deae2f1268dfda14999a4d14d0d0c5
- https://git.kernel.org/stable/c/98e55b0b876bde3353f4e074883d66ecb55c65a3
- https://git.kernel.org/stable/c/9ad1981fc4de3afb7db3e8eb5a6a52d4c7d0d577
- https://git.kernel.org/stable/c/9d5e96cc1f1720019ce27b127a31695148d38bb0
- https://git.kernel.org/stable/c/b5dca2cd3f0239512da808598b4e70557eb4c2a1
- https://git.kernel.org/stable/c/b8ce58ab80faaea015c206382041ff3bcf5495ff
- https://git.kernel.org/stable/c/d7e30dfc166d33470bba31a42f9bbc346e5409d5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49326.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49326
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
