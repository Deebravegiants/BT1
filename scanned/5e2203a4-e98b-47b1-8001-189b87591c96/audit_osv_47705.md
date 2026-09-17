# [M] CVE-2017-1000380

## Summary
Severity: Medium
Advisory: CVE-2017-1000380
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2017-06-17
Source: https://osv.dev/vulnerability/CVE-2017-1000380
Type: osv

## Details
sound/core/timer.c in the Linux kernel before 4.11.5 is vulnerable to a data race in the ALSA /dev/snd/timer driver resulting in local users being able to read information belonging to other users, i.e., uninitialized memory contents may be disclosed when a read and an ioctl happen at the same time.

## References
- https://source.android.com/security/bulletin/pixel/2017-12-01
- http://www.debian.org/security/2017/dsa-3981
- http://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.11.5
- https://access.redhat.com/errata/RHSA-2017:3315
- https://access.redhat.com/errata/RHSA-2017:3322
- http://www.securityfocus.com/bid/99121
- https://access.redhat.com/errata/RHSA-2017:3295
- http://www.openwall.com/lists/oss-security/2017/06/12/2
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=ba3021b2c79b2fa9114f92790a99deb27a65b728
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=d11662f4f798b50d8c8743f433842c3e40fe3378
- https://github.com/torvalds/linux/commit/ba3021b2c79b2fa9114f92790a99deb27a65b728
- https://github.com/torvalds/linux/commit/d11662f4f798b50d8c8743f433842c3e40fe3378
