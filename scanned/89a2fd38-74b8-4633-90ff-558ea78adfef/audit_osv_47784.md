# [H] CVE-2017-12146

## Summary
Severity: High
Advisory: CVE-2017-12146
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-09-08
Source: https://osv.dev/vulnerability/CVE-2017-12146
Type: osv

## Details
The driver_override implementation in drivers/base/platform.c in the Linux kernel before 4.12.1 allows local users to gain privileges by leveraging a race condition between a read operation and a store operation that involve different overrides.

## References
- http://www.debian.org/security/2017/dsa-3981
- http://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.12.1
- http://www.securityfocus.com/bid/100651
- https://bugzilla.redhat.com/show_bug.cgi?id=1489078
- https://bugzilla.suse.com/show_bug.cgi?id=1057474
- https://github.com/torvalds/linux/commit/6265539776a0810b7ce6398c27866ddb9c6bd154
- https://source.android.com/security/bulletin/2017-09-01
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=6265539776a0810b7ce6398c27866ddb9c6bd154
