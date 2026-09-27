# [H] CVE-2017-13711

## Summary
Severity: High
Advisory: CVE-2017-13711
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-09-01
Source: https://osv.dev/vulnerability/CVE-2017-13711
Type: osv

## Details
Use-after-free vulnerability in the sofree function in slirp/socket.c in QEMU (aka Quick Emulator) allows attackers to cause a denial of service (QEMU instance crash) by leveraging failure to properly clear ifq_so from pending packets.

## References
- http://www.debian.org/security/2017/dsa-3991
- http://www.securityfocus.com/bid/100534
- https://access.redhat.com/errata/RHSA-2018:0816
- https://access.redhat.com/errata/RHSA-2018:1104
- https://access.redhat.com/errata/RHSA-2018:1113
- http://www.openwall.com/lists/oss-security/2017/08/29/6
- https://bugzilla.redhat.com/show_bug.cgi?id=1486400
- https://lists.gnu.org/archive/html/qemu-devel/2017-08/msg05201.html
