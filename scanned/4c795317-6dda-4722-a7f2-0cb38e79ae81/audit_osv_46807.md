# [M] CVE-2015-4170

## Summary
Severity: Medium
Advisory: CVE-2015-4170
CVSS: 4.7 (CVSS:3.0/AV:L/AC:H/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2016-05-02
Source: https://osv.dev/vulnerability/CVE-2015-4170
Type: osv

## Details
Race condition in the ldsem_cmpxchg function in drivers/tty/tty_ldsem.c in the Linux kernel before 3.13-rc4-next-20131218 allows local users to cause a denial of service (ldsem_down_read and ldsem_down_write deadlock) by establishing a new tty thread during shutdown of a previous tty thread.

## References
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=cf872776fc84128bb779ce2b83a37c884c3203ae
- https://access.redhat.com/errata/RHSA-2016:1395
- https://bugzilla.redhat.com/show_bug.cgi?id=1218879
- https://github.com/torvalds/linux/commit/cf872776fc84128bb779ce2b83a37c884c3203ae
- https://www.kernel.org/pub/linux/kernel/next/patch-v3.13-rc4-next-20131218.xz
- https://bugzilla.redhat.com/show_bug.cgi?id=1218879
- http://www.openwall.com/lists/oss-security/2015/05/26/1
- http://www.oracle.com/technetwork/topics/security/linuxbulletinoct2015-2719645.html
- http://www.securityfocus.com/bid/74820
