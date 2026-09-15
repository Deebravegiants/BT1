# [H] CVE-2017-7184

## Summary
Severity: High
Advisory: CVE-2017-7184
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-03-19
Source: https://osv.dev/vulnerability/CVE-2017-7184
Type: osv

## Details
The xfrm_replay_verify_len function in net/xfrm/xfrm_user.c in the Linux kernel through 4.10.6 does not validate certain size data after an XFRM_MSG_NEWAE update, which allows local users to obtain root privileges or cause a denial of service (heap-based out-of-bounds access) by leveraging the CAP_NET_ADMIN capability, as demonstrated during a Pwn2Own competition at CanSecWest 2017 for the Ubuntu 16.10 linux-image-* package 4.8.0.41.52.

## References
- https://access.redhat.com/errata/RHSA-2017:2931
- https://github.com/torvalds/linux/commit/f843ee6dd019bcece3e74e76ad9df0155655d0df
- http://www.securitytracker.com/id/1038166
- https://github.com/torvalds/linux/commit/677e806da4d916052585301785d847c3b3e6186a
- https://twitter.com/thezdi/status/842126074435665920
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=f843ee6dd019bcece3e74e76ad9df0155655d0df
- http://openwall.com/lists/oss-security/2017/03/29/2
- http://www.eweek.com/security/ubuntu-linux-falls-on-day-1-of-pwn2own-hacking-competition
- https://access.redhat.com/errata/RHSA-2017:2918
- https://blog.trendmicro.com/results-pwn2own-2017-day-one/
- https://source.android.com/security/bulletin/2017-05-01
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=677e806da4d916052585301785d847c3b3e6186a
- http://www.securityfocus.com/bid/97018
- https://access.redhat.com/errata/RHSA-2017:2930
- https://access.redhat.com/errata/RHSA-2019:4159
