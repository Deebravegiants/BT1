# [M] CVE-2023-47233

## Summary
Severity: Medium
Advisory: CVE-2023-47233
CVSS: 4.3 (CVSS:3.1/AV:P/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-11-03
Source: https://osv.dev/vulnerability/CVE-2023-47233
Type: osv

## Details
The brcm80211 component in the Linux kernel through 6.5.10 has a brcmf_cfg80211_detach use-after-free in the device unplugging (disconnect the USB by hotplug) code. For physically proximate attackers with local access, this "could be exploited in a real world scenario." This is related to brcmf_cfg80211_escan_timeout_worker in drivers/net/wireless/broadcom/brcm80211/brcmfmac/cfg80211.c.

## References
- https://lists.debian.org/debian-lts-announce/2024/06/msg00020.html
- https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=0f7352557a35ab7888bc7831411ec8a3cbe20d78
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://bugzilla.suse.com/show_bug.cgi?id=1216702
- https://lore.kernel.org/all/20231104054709.716585-1-zyytlz.wz%40163.com/
- https://marc.info/?l=linux-kernel&m=169907678011243&w=2
