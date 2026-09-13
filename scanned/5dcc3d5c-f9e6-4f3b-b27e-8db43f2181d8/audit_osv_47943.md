# [H] CVE-2017-15265

## Summary
Severity: High
Advisory: CVE-2017-15265
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-10-16
Source: https://osv.dev/vulnerability/CVE-2017-15265
Type: osv

## Details
Race condition in the ALSA subsystem in the Linux kernel before 4.13.8 allows local users to cause a denial of service (use-after-free) or possibly have unspecified other impact via crafted /dev/snd/seq ioctl calls, related to sound/core/seq/seq_clientmgr.c and sound/core/seq/seq_ports.c.

## References
- http://www.securitytracker.com/id/1039561
- https://access.redhat.com/errata/RHSA-2018:0676
- https://access.redhat.com/errata/RHSA-2018:1062
- https://access.redhat.com/errata/RHSA-2018:1170
- https://lists.debian.org/debian-lts-announce/2017/12/msg00004.html
- https://usn.ubuntu.com/3698-1/
- http://www.securityfocus.com/bid/101288
- https://access.redhat.com/errata/RHSA-2018:1130
- https://access.redhat.com/errata/RHSA-2018:3823
- https://help.ecostruxureit.com/display/public/UADCE725/Security+fixes+in+StruxureWare+Data+Center+Expert+v7.6.0
- https://source.android.com/security/bulletin/2018-02-01
- https://usn.ubuntu.com/3698-2/
- https://www.oracle.com/security-alerts/cpujul2020.html
- http://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.13.8
- https://access.redhat.com/errata/RHSA-2018:2390
- https://access.redhat.com/errata/RHSA-2018:3822
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=71105998845fb012937332fe2e806d443c09e026
- http://mailman.alsa-project.org/pipermail/alsa-devel/2017-October/126292.html
- http://www.openwall.com/lists/oss-security/2017/10/11/3
- https://bugzilla.suse.com/show_bug.cgi?id=1062520
