# [H] CVE-2015-3288

## Summary
Severity: High
Advisory: CVE-2015-3288
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-10-16
Source: https://osv.dev/vulnerability/CVE-2015-3288
Type: osv

## Details
mm/memory.c in the Linux kernel before 4.1.4 mishandles anonymous pages, which allows local users to gain privileges or cause a denial of service (page tainting) via a crafted application that triggers writing to page zero.

## References
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=6b7339f4c31ad69c8e9c0b2859276e22cf72176d
- http://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.1.4
- http://www.securityfocus.com/bid/93591
- https://bugzilla.redhat.com/show_bug.cgi?id=1333830
- https://github.com/torvalds/linux/commit/6b7339f4c31ad69c8e9c0b2859276e22cf72176d
- https://security-tracker.debian.org/tracker/CVE-2015-3288
- https://source.android.com/security/bulletin/2017-01-01.html
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=6b7339f4c31ad69c8e9c0b2859276e22cf72176d
- https://bugzilla.redhat.com/show_bug.cgi?id=1333830
- https://bugzilla.redhat.com/show_bug.cgi?id=1333830
