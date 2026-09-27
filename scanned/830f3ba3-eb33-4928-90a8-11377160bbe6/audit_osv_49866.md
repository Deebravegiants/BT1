# [M] CVE-2019-20096

## Summary
Severity: Medium
Advisory: CVE-2019-20096
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-12-30
Source: https://osv.dev/vulnerability/CVE-2019-20096
Type: osv

## Details
In the Linux kernel before 5.1, there is a memory leak in __feat_register_sp() in net/dccp/feat.c, which may cause denial of service, aka CID-1d3ff0950e2b.

## References
- https://usn.ubuntu.com/4285-1/
- https://usn.ubuntu.com/4286-1/
- http://packetstormsecurity.com/files/156455/Kernel-Live-Patch-Security-Notice-LSN-0063-1.html
- https://usn.ubuntu.com/4286-2/
- https://usn.ubuntu.com/4287-1/
- https://usn.ubuntu.com/4287-2/
- http://lists.opensuse.org/opensuse-security-announce/2020-03/msg00021.html
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.1
- https://lists.debian.org/debian-lts-announce/2020/03/msg00001.html
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=1d3ff0950e2b40dc861b1739029649d03f591820
