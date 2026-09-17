# [H] CVE-2017-5970

## Summary
Severity: High
Advisory: CVE-2017-5970
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-02-14
Source: https://osv.dev/vulnerability/CVE-2017-5970
Type: osv

## Details
The ipv4_pktinfo_prepare function in net/ipv4/ip_sockglue.c in the Linux kernel through 4.9.9 allows attackers to cause a denial of service (system crash) via (1) an application that makes crafted system calls or possibly (2) IPv4 traffic with invalid IP options.

## References
- http://www.securityfocus.com/bid/96233
- https://source.android.com/security/bulletin/2017-07-01
- http://www.debian.org/security/2017/dsa-3791
- https://access.redhat.com/errata/RHSA-2017:1842
- https://access.redhat.com/errata/RHSA-2017:2077
- https://access.redhat.com/errata/RHSA-2017:2669
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=34b2cef20f19c87999fff3da4071e66937db9644
- https://bugzilla.redhat.com/show_bug.cgi?id=1421638
- https://github.com/torvalds/linux/commit/34b2cef20f19c87999fff3da4071e66937db9644
- https://patchwork.ozlabs.org/patch/724136/
- http://www.openwall.com/lists/oss-security/2017/02/12/3
