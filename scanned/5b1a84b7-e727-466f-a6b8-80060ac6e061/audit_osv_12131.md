# [M] CVE-2018-1049

## Summary
Severity: Medium
Advisory: CVE-2018-1049
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-02-16
Source: https://osv.dev/vulnerability/CVE-2018-1049
Type: osv

## Details
In systemd prior to 234 a race condition exists between .mount and .automount units such that automount requests from kernel may not be serviced by systemd resulting in kernel holding the mountpoint and any processes that try to use said mount will hang. A race condition like this may lead to denial of service, until mount points are unmounted.

## References
- http://www.securitytracker.com/id/1041520
- https://access.redhat.com/errata/RHSA-2018:0260
- https://lists.debian.org/debian-lts-announce/2018/11/msg00017.html
- https://usn.ubuntu.com/3558-1/
- https://bugzilla.redhat.com/show_bug.cgi?id=1534701
