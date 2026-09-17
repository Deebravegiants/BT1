# [H] CVE-2013-4535

## Summary
Severity: High
Advisory: CVE-2013-4535
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2020-02-11
Source: https://osv.dev/vulnerability/CVE-2013-4535
Type: osv

## Details
The virtqueue_map_sg function in hw/virtio/virtio.c in QEMU before 1.7.2 allows remote attackers to execute arbitrary files via a crafted savevm image, related to virtio-block or virtio-serial read.

## References
- http://lists.fedoraproject.org/pipermail/package-announce/2014-May/133345.html
- http://lists.nongnu.org/archive/html/qemu-stable/2014-07/msg00187.html
- http://rhn.redhat.com/errata/RHSA-2014-0743.html
- http://rhn.redhat.com/errata/RHSA-2014-0744.html
- https://bugzilla.redhat.com/show_bug.cgi?id=1066401
- https://bugzilla.redhat.com/show_bug.cgi?id=1066401
- http://git.qemu.org/?p=qemu.git%3Ba=commitdiff%3Bh=36cf2a37132c7f01fa9adb5f95f5312b27742fd4
