# [H] CVE-2023-1380

## Summary
Severity: High
Advisory: CVE-2023-1380
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2023-03-27
Source: https://osv.dev/vulnerability/CVE-2023-1380
Type: osv

## Details
A slab-out-of-bound read problem was found in brcmf_get_assoc_ies in drivers/net/wireless/broadcom/brcm80211/brcmfmac/cfg80211.c in the Linux Kernel. This issue could occur when assoc_info->req_len data is bigger than the size of the buffer, defined as WL_EXTRA_BUF_MAX, leading to a denial of service.

## References
- https://lists.debian.org/debian-lts-announce/2023/07/msg00030.html
- https://www.debian.org/security/2023/dsa-5480
- http://packetstormsecurity.com/files/173757/Kernel-Live-Patch-Security-Notice-LSN-0096-1.html
- https://lists.debian.org/debian-lts-announce/2023/10/msg00027.html
- https://security.netapp.com/advisory/ntap-20230511-0001/
- https://www.openwall.com/lists/oss-security/2023/03/14/1
- http://packetstormsecurity.com/files/173087/Kernel-Live-Patch-Security-Notice-LSN-0095-1.html
- https://bugzilla.redhat.com/show_bug.cgi?id=2177883
- https://lore.kernel.org/linux-wireless/20230309104457.22628-1-jisoo.jang%40yonsei.ac.kr/T/#u
