# [M] CVE-2016-5403

## Summary
Severity: Medium
Advisory: CVE-2016-5403
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-08-02
Source: https://osv.dev/vulnerability/CVE-2016-5403
Type: osv

## Details
The virtqueue_pop function in hw/virtio/virtio.c in QEMU allows local guest OS administrators to cause a denial of service (memory consumption and QEMU process crash) by submitting requests without waiting for completion.

## References
- http://rhn.redhat.com/errata/RHSA-2016-1585.html
- http://rhn.redhat.com/errata/RHSA-2016-1586.html
- http://rhn.redhat.com/errata/RHSA-2016-1606.html
- http://rhn.redhat.com/errata/RHSA-2016-1607.html
- http://rhn.redhat.com/errata/RHSA-2016-1652.html
- http://rhn.redhat.com/errata/RHSA-2016-1653.html
- http://rhn.redhat.com/errata/RHSA-2016-1654.html
- http://rhn.redhat.com/errata/RHSA-2016-1655.html
- http://rhn.redhat.com/errata/RHSA-2016-1756.html
- http://rhn.redhat.com/errata/RHSA-2016-1763.html
- http://rhn.redhat.com/errata/RHSA-2016-1943.html
- http://www.oracle.com/technetwork/topics/security/linuxbulletinjul2016-3090544.html
- http://www.oracle.com/technetwork/topics/security/linuxbulletinoct2016-3090545.html
- http://www.oracle.com/technetwork/topics/security/ovmbulletinjul2016-3090546.html
- http://www.securityfocus.com/bid/92148
- http://www.securitytracker.com/id/1036476
- http://www.ubuntu.com/usn/USN-3047-1
- http://www.ubuntu.com/usn/USN-3047-2
- https://lists.debian.org/debian-lts-announce/2019/09/msg00021.html
- https://bugzilla.redhat.com/show_bug.cgi?id=1358359
