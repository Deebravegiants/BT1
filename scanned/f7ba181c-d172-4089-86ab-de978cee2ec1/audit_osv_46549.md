# [H] CVE-2013-2596

## Summary
Severity: High
Advisory: CVE-2013-2596
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2013-04-13
Source: https://osv.dev/vulnerability/CVE-2013-2596
Type: osv

## Details
Integer overflow in the fb_mmap function in drivers/video/fbmem.c in the Linux kernel before 3.8.9, as used in a certain Motorola build of Android 4.1.2 and other products, allows local users to create a read-write memory mapping for the entirety of kernel memory, and consequently gain privileges, via crafted /dev/graphics/fb0 mmap2 system calls, as demonstrated by the Motochopper pwn program.

## References
- http://kb.juniper.net/InfoCenter/index?page=content&id=JSA10761
- http://marc.info/?l=linux-kernel&m=136616837923938&w=2
- http://rhn.redhat.com/errata/RHSA-2015-0695.html
- http://rhn.redhat.com/errata/RHSA-2015-0782.html
- http://rhn.redhat.com/errata/RHSA-2015-0803.html
- http://www.droid-life.com/2013/04/09/root-method-released-for-droid-razr-hd-running-android-4-1-2-other-devices-too/
- http://www.kernel.org/pub/linux/kernel/v3.x/ChangeLog-3.8.9
- http://www.mandriva.com/security/advisories?name=MDVSA-2013:176
- http://www.oracle.com/technetwork/topics/security/linuxbulletinjan2016-2867209.html
- http://www.securityfocus.com/bid/59264
- http://marc.info/?l=linux-kernel&m=136616837923938&w=2
- http://www.kernel.org/pub/linux/kernel/v3.x/ChangeLog-3.8.9
- http://forum.xda-developers.com/showthread.php?t=2255491
- http://www.droid-life.com/2013/04/09/root-method-released-for-droid-razr-hd-running-android-4-1-2-other-devices-too/
- http://www.droidrzr.com/index.php/topic/15208-root-motochopper-yet-another-android-root-exploit/
- https://github.com/torvalds/linux/commit/fc9bbca8f650e5f738af8806317c0a041a48ae4a
- http://marc.info/?l=linux-kernel&m=136616837923938&w=2
- http://www.oracle.com/technetwork/topics/security/linuxbulletinjan2016-2867209.html
- https://github.com/torvalds/linux/commit/b4cbb197c7e7a68dbad0d491242e3ca67420c13e
- https://github.com/torvalds/linux/commit/fc9bbca8f650e5f738af8806317c0a041a48ae4a
