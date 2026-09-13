# [H] CVE-2017-15868

## Summary
Severity: High
Advisory: CVE-2017-15868
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-12-05
Source: https://osv.dev/vulnerability/CVE-2017-15868
Type: osv

## Details
The bnep_add_connection function in net/bluetooth/bnep/core.c in the Linux kernel before 3.19 does not ensure that an l2cap socket is available, which allows local users to gain privileges via a crafted application.

## References
- http://lists.opensuse.org/opensuse-security-announce/2018-01/msg00007.html
- https://source.android.com/security/bulletin/pixel/2017-12-01
- https://www.debian.org/security/2018/dsa-4082
- http://www.securityfocus.com/bid/102084
- https://lists.debian.org/debian-lts-announce/2017/12/msg00004.html
- https://usn.ubuntu.com/3583-1/
- https://usn.ubuntu.com/3583-2/
- https://github.com/torvalds/linux/commit/71bb99a02b32b4cc4265118e85f6035ca72923f0
- https://patchwork.kernel.org/patch/9882449/
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=71bb99a02b32b4cc4265118e85f6035ca72923f0
