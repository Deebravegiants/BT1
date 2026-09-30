# [H] CVE-2023-4622

## Summary
Severity: High
Advisory: CVE-2023-4622
Aliases: A-299123598, ASB-A-299123598
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-09-06
Source: https://osv.dev/vulnerability/CVE-2023-4622
Type: osv

## Details
A use-after-free vulnerability in the Linux kernel's af_unix component can be exploited to achieve local privilege escalation.

The unix_stream_sendpage() function tries to add data to the last skb in the peer's recv queue without locking the queue. Thus there is a race where unix_stream_sendpage() could access an skb locklessly that is being released by garbage collection, resulting in use-after-free.

We recommend upgrading past commit 790c2f9d15b594350ae9bca7b236f2b1859de02c.

## References
- http://packetstormsecurity.com/files/175963/Kernel-Live-Patch-Security-Notice-LSN-0099-1.html
- https://lists.debian.org/debian-lts-announce/2024/01/msg00004.html
- https://www.debian.org/security/2023/dsa-5492
- https://lists.debian.org/debian-lts-announce/2023/10/msg00027.html
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git/commit/?h=linux-6.1.y&id=790c2f9d15b594350ae9bca7b236f2b1859de02c
- https://kernel.dance/790c2f9d15b594350ae9bca7b236f2b1859de02c
