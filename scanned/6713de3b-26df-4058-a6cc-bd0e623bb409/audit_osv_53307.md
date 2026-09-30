# [H] CVE-2022-36946

## Summary
Severity: High
Advisory: CVE-2022-36946
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-07-27
Source: https://osv.dev/vulnerability/CVE-2022-36946
Type: osv

## Details
nfqnl_mangle in net/netfilter/nfnetlink_queue.c in the Linux kernel through 5.18.14 allows remote attackers to cause a denial of service (panic) because, in the case of an nf_queue verdict with a one-byte nfta_payload attribute, an skb_pull can encounter a negative skb->len.

## References
- https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=99a63d36cb3ed5ca3aa6fcb64cffbeaf3b0fb164
- https://security.netapp.com/advisory/ntap-20220901-0007/
- https://www.debian.org/security/2022/dsa-5207
- https://lists.debian.org/debian-lts-announce/2022/09/msg00011.html
- https://lists.debian.org/debian-lts-announce/2022/10/msg00000.html
- https://marc.info/?l=netfilter-devel&m=165883202007292&w=2
