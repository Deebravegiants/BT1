# [H] CVE-2017-7533

## Summary
Severity: High
Advisory: CVE-2017-7533
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-08-05
Source: https://osv.dev/vulnerability/CVE-2017-7533
Type: osv

## Details
Race condition in the fsnotify implementation in the Linux kernel through 4.12.4 allows local users to gain privileges or cause a denial of service (memory corruption) via a crafted application that leverages simultaneous execution of the inotify_handle_event and vfs_rename functions.

## References
- https://access.redhat.com/errata/RHSA-2017:2869
- http://www.openwall.com/lists/oss-security/2019/06/28/2
- http://www.securityfocus.com/bid/100123
- https://access.redhat.com/errata/RHSA-2017:2585
- https://www.mail-archive.com/linux-kernel%40vger.kernel.org/msg1408967.html
- http://www.debian.org/security/2017/dsa-3927
- http://www.debian.org/security/2017/dsa-3945
- http://www.openwall.com/lists/oss-security/2019/06/28/1
- http://www.securitytracker.com/id/1039075
- https://access.redhat.com/errata/RHSA-2017:2473
- https://source.android.com/security/bulletin/2017-12-01
- http://www.openwall.com/lists/oss-security/2019/06/27/7
- https://access.redhat.com/errata/RHSA-2017:2669
- https://access.redhat.com/errata/RHSA-2017:2770
- https://github.com/torvalds/linux/commit/49d31c2f389acfe83417083e1208422b4091cd9e
- https://patchwork.kernel.org/patch/9755757/
- https://bugzilla.redhat.com/show_bug.cgi?id=1468283
- https://patchwork.kernel.org/patch/9755753/
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=49d31c2f389acfe83417083e1208422b4091cd9e
- http://openwall.com/lists/oss-security/2017/08/03/2
