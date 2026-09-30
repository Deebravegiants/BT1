# [C] CVE-2018-17963

## Summary
Severity: Critical
Advisory: CVE-2018-17963
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-10-09
Source: https://osv.dev/vulnerability/CVE-2018-17963
Type: osv

## Details
qemu_deliver_packet_iov in net/net.c in Qemu accepts packet sizes greater than INT_MAX, which allows attackers to cause a denial of service or possibly have unspecified other impact.

## References
- http://www.openwall.com/lists/oss-security/2018/10/08/1
- https://access.redhat.com/errata/RHSA-2019:2166
- https://access.redhat.com/errata/RHSA-2019:2425
- https://access.redhat.com/errata/RHSA-2019:2553
- https://lists.debian.org/debian-lts-announce/2018/11/msg00038.html
- https://usn.ubuntu.com/3826-1/
- https://www.debian.org/security/2018/dsa-4338
- https://lists.gnu.org/archive/html/qemu-devel/2018-09/msg03267.html
- https://lists.gnu.org/archive/html/qemu-devel/2018-11/msg06054.html
