# [H] CVE-2017-10661

## Summary
Severity: High
Advisory: CVE-2017-10661
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-08-19
Source: https://osv.dev/vulnerability/CVE-2017-10661
Type: osv

## Details
Race condition in fs/timerfd.c in the Linux kernel before 4.10.15 allows local users to gain privileges or cause a denial of service (list corruption or use-after-free) via simultaneous file-descriptor operations that leverage improper might_cancel queueing.

## References
- http://www.debian.org/security/2017/dsa-3981
- http://www.securityfocus.com/bid/100215
- https://www.exploit-db.com/exploits/43345/
- http://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.10.15
- https://access.redhat.com/errata/RHSA-2018:3083
- https://access.redhat.com/errata/RHSA-2018:3096
- https://access.redhat.com/errata/RHSA-2019:4057
- https://access.redhat.com/errata/RHSA-2019:4058
- https://access.redhat.com/errata/RHSA-2020:0036
- https://bugzilla.redhat.com/show_bug.cgi?id=1481136
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=1e38da300e1e395a15048b0af1e5305bd91402f6
- https://github.com/torvalds/linux/commit/1e38da300e1e395a15048b0af1e5305bd91402f6
- https://source.android.com/security/bulletin/2017-08-01
