# [M] CVE-2015-5278

## Summary
Severity: Medium
Advisory: CVE-2015-5278
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-01-23
Source: https://osv.dev/vulnerability/CVE-2015-5278
Type: osv

## Details
The ne2000_receive function in hw/net/ne2000.c in QEMU before 2.4.0.1 allows attackers to cause a denial of service (infinite loop and instance crash) or possibly execute arbitrary code via vectors related to receiving packets.

## References
- http://lists.fedoraproject.org/pipermail/package-announce/2015-October/168077.html
- http://lists.fedoraproject.org/pipermail/package-announce/2015-October/168646.html
- http://lists.fedoraproject.org/pipermail/package-announce/2015-October/168671.html
- http://www.openwall.com/lists/oss-security/2015/09/15/2
- http://www.ubuntu.com/usn/USN-2745-1
- https://lists.gnu.org/archive/html/qemu-devel/2015-09/msg03985.html
- https://lists.gnu.org/archive/html/qemu-devel/2015-09/msg05832.html
- https://www.arista.com/en/support/advisories-notices/security-advisories/1188-security-advisory-14
- http://lists.fedoraproject.org/pipermail/package-announce/2015-October/168077.html
- http://lists.fedoraproject.org/pipermail/package-announce/2015-October/168646.html
- http://lists.fedoraproject.org/pipermail/package-announce/2015-October/168671.html
- http://www.openwall.com/lists/oss-security/2015/09/15/2
- https://lists.gnu.org/archive/html/qemu-devel/2015-09/msg03985.html
- https://lists.gnu.org/archive/html/qemu-devel/2015-09/msg05832.html
- http://www.openwall.com/lists/oss-security/2015/09/15/2
- https://lists.gnu.org/archive/html/qemu-devel/2015-09/msg03985.html
