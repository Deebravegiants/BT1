# [H] CVE-2018-1064

## Summary
Severity: High
Advisory: CVE-2018-1064
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-03-28
Source: https://osv.dev/vulnerability/CVE-2018-1064
Type: osv

## Details
libvirt version before 4.2.0-rc1 is vulnerable to a resource exhaustion as a result of an incomplete fix for CVE-2018-5748 that affects QEMU monitor but now also triggered via QEMU guest agent.

## References
- https://libvirt.org/git/?p=libvirt.git%3Ba=commit%3Bh=fbf31e1a4cd19d6f6e33e0937a009775cd7d9513
- https://usn.ubuntu.com/3680-1/
- https://access.redhat.com/errata/RHSA-2018:1396
- https://access.redhat.com/errata/RHSA-2018:1929
- https://lists.debian.org/debian-lts-announce/2018/03/msg00018.html
- https://www.debian.org/security/2018/dsa-4137
- https://bugzilla.redhat.com/show_bug.cgi?id=1550672
