# [H] Out-of-bounds write in Linux kernel's ipvlan network driver

## Summary
Severity: High
Advisory: CVE-2023-3090
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-06-28
Source: https://osv.dev/vulnerability/CVE-2023-3090
Type: osv

## Details
A heap out-of-bounds write vulnerability in the Linux Kernel ipvlan network driver can be exploited to achieve local privilege escalation.

The out-of-bounds write is caused by missing skb->cb  initialization in the ipvlan network driver. The vulnerability is reachable if CONFIG_IPVLAN is enabled.


We recommend upgrading past commit 90cbed5247439a966b645b34eb0a2e037836ea8e.

## References
- http://packetstormsecurity.com/files/174577/Kernel-Live-Patch-Security-Notice-LSN-0097-1.html
- http://packetstormsecurity.com/files/175072/Kernel-Live-Patch-Security-Notice-LSN-0098-1.html
- https://git.kernel.org
- https://kernel.dance/90cbed5247439a966b645b34eb0a2e037836ea8e
- https://lists.debian.org/debian-lts-announce/2023/07/msg00030.html
- https://lists.debian.org/debian-lts-announce/2023/10/msg00027.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/3xxx/CVE-2023-3090.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-3090
- https://security.netapp.com/advisory/ntap-20230731-0002/
- https://www.debian.org/security/2023/dsa-5448
- https://www.debian.org/security/2023/dsa-5480
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=90cbed5247439a966b645b34eb0a2e037836ea8e
