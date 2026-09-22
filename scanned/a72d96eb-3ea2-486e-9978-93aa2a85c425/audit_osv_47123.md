# [M] CVE-2015-8970

## Summary
Severity: Medium
Advisory: CVE-2015-8970
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-11-28
Source: https://osv.dev/vulnerability/CVE-2015-8970
Type: osv

## Details
crypto/algif_skcipher.c in the Linux kernel before 4.4.2 does not verify that a setkey operation has been performed on an AF_ALG socket before an accept system call is processed, which allows local users to cause a denial of service (NULL pointer dereference and system crash) via a crafted application that does not supply a key, related to the lrw_crypt function in crypto/lrw.c.

## References
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=dd504589577d8e8e70f51f997ad487a4cb6c026f
- http://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.2
- http://www.openwall.com/lists/oss-security/2016/11/04/3
- http://www.securityfocus.com/bid/94217
- https://access.redhat.com/errata/RHSA-2017:1842
- https://access.redhat.com/errata/RHSA-2017:2077
- https://access.redhat.com/errata/RHSA-2017:2437
- https://access.redhat.com/errata/RHSA-2017:2444
- https://github.com/torvalds/linux/commit/dd504589577d8e8e70f51f997ad487a4cb6c026f
- http://www.openwall.com/lists/oss-security/2016/11/04/3
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=dd504589577d8e8e70f51f997ad487a4cb6c026f
- https://github.com/torvalds/linux/commit/dd504589577d8e8e70f51f997ad487a4cb6c026f
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=dd504589577d8e8e70f51f997ad487a4cb6c026f
- https://bugzilla.redhat.com/show_bug.cgi?id=1386286
- https://github.com/torvalds/linux/commit/dd504589577d8e8e70f51f997ad487a4cb6c026f
- https://groups.google.com/forum/#%21msg/syzkaller/frb2XrB5aWk/xCXzkIBcDAAJ
