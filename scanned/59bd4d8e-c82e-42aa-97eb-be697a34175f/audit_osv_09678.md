# [H] CVE-2017-10664

## Summary
Severity: High
Advisory: CVE-2017-10664
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-08-02
Source: https://osv.dev/vulnerability/CVE-2017-10664
Type: osv

## Details
qemu-nbd in QEMU (aka Quick Emulator) does not ignore SIGPIPE, which allows remote attackers to cause a denial of service (daemon crash) by disconnecting during a server-to-client reply attempt.

## References
- http://www.debian.org/security/2017/dsa-3920
- http://www.securityfocus.com/bid/99513
- https://access.redhat.com/errata/RHSA-2017:2390
- https://access.redhat.com/errata/RHSA-2017:2445
- https://access.redhat.com/errata/RHSA-2017:3466
- https://access.redhat.com/errata/RHSA-2017:3470
- https://access.redhat.com/errata/RHSA-2017:3471
- https://access.redhat.com/errata/RHSA-2017:3472
- https://access.redhat.com/errata/RHSA-2017:3473
- https://access.redhat.com/errata/RHSA-2017:3474
- https://lists.debian.org/debian-lts-announce/2018/11/msg00038.html
- http://www.openwall.com/lists/oss-security/2017/06/29/1
- https://bugzilla.redhat.com/show_bug.cgi?id=1466190
- https://lists.gnu.org/archive/html/qemu-devel/2017-06/msg02693.html
