# [M] CVE-2020-25211

## Summary
Severity: Medium
Advisory: CVE-2020-25211
CVSS: 6.0 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:N/I:H/A:H)
Published: 2020-09-09
Source: https://osv.dev/vulnerability/CVE-2020-25211
Type: osv

## Details
In the Linux kernel through 5.8.7, local attackers able to inject conntrack netlink configuration could overflow a local buffer, causing crashes or triggering use of incorrect protocol numbers in ctnetlink_parse_tuple_filter in net/netfilter/nf_conntrack_netlink.c, aka CID-1cc5ef91d2ff.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/OLDYVOM4OS55HA45Y3UEVLDHYGFXPZUX/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/BL2O4JAMPJG4YMLLJ7JFDHDJRXN4RKTC/
- https://security.netapp.com/advisory/ntap-20201009-0001/
- https://twitter.com/grsecurity/status/1303646421158109185
- https://www.debian.org/security/2020/dsa-4774
- https://lists.debian.org/debian-lts-announce/2020/10/msg00028.html
- https://lists.debian.org/debian-lts-announce/2020/10/msg00032.html
- https://lists.debian.org/debian-lts-announce/2020/10/msg00034.html
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=1cc5ef91d2ff94d2bf2de3b3585423e8a1051cb6
