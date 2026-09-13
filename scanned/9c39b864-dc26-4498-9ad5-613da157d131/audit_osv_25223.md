# [H] CVE-2023-32233

## Summary
Severity: High
Advisory: CVE-2023-32233
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-05-08
Source: https://osv.dev/vulnerability/CVE-2023-32233
Type: osv

## Details
In the Linux kernel through 6.3.1, a use-after-free in Netfilter nf_tables when processing batch requests can be abused to perform arbitrary read and write operations on kernel memory. Unprivileged local users can obtain root privileges. This occurs because anonymous sets are mishandled.

## References
- https://lists.debian.org/debian-lts-announce/2023/07/msg00030.html
- http://www.openwall.com/lists/oss-security/2023/05/15/5
- https://lists.debian.org/debian-lts-announce/2023/06/msg00008.html
- https://security.netapp.com/advisory/ntap-20230616-0002/
- https://www.debian.org/security/2023/dsa-5402
- https://bugzilla.redhat.com/show_bug.cgi?id=2196105
- https://news.ycombinator.com/item?id=35879660
- http://packetstormsecurity.com/files/173087/Kernel-Live-Patch-Security-Notice-LSN-0095-1.html
- https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=c1592a89942e9678f7d9c8030efa777c0d57edab
- https://github.com/torvalds/linux/commit/c1592a89942e9678f7d9c8030efa777c0d57edab
- https://www.openwall.com/lists/oss-security/2023/05/08/4
