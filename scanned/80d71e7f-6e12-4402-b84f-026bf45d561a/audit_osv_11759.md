# [H] CVE-2017-9524

## Summary
Severity: High
Advisory: CVE-2017-9524
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-07-06
Source: https://osv.dev/vulnerability/CVE-2017-9524
Type: osv

## Details
The qemu-nbd server in QEMU (aka Quick Emulator), when built with the Network Block Device (NBD) Server support, allows remote attackers to cause a denial of service (segmentation fault and server crash) by leveraging failure to ensure that all initialization occurs before talking to a client in the nbd_negotiate function.

## References
- http://www.debian.org/security/2017/dsa-3925
- http://www.securityfocus.com/bid/99011
- https://access.redhat.com/errata/RHSA-2017:1681
- https://access.redhat.com/errata/RHSA-2017:1682
- https://access.redhat.com/errata/RHSA-2017:2408
- http://www.openwall.com/lists/oss-security/2017/06/12/1
- https://lists.gnu.org/archive/html/qemu-devel/2017-05/msg06240.html
- https://lists.gnu.org/archive/html/qemu-devel/2017-06/msg02321.html
