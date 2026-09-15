# [M] CVE-2016-3712

## Summary
Severity: Medium
Advisory: CVE-2016-3712
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-05-11
Source: https://osv.dev/vulnerability/CVE-2016-3712
Type: osv

## Details
Integer overflow in the VGA module in QEMU allows local guest OS users to cause a denial of service (out-of-bounds read and QEMU process crash) by editing VGA registers in VBE mode.

## References
- http://rhn.redhat.com/errata/RHSA-2016-2585.html
- http://rhn.redhat.com/errata/RHSA-2017-0621.html
- http://support.citrix.com/article/CTX212736
- http://www.debian.org/security/2016/dsa-3573
- http://www.openwall.com/lists/oss-security/2016/05/09/4
- http://www.oracle.com/technetwork/topics/security/ovmbulletinjul2016-3090546.html
- http://www.securityfocus.com/bid/90314
- http://www.securitytracker.com/id/1035794
- http://www.ubuntu.com/usn/USN-2974-1
- http://xenbits.xen.org/xsa/advisory-179.html
- https://lists.gnu.org/archive/html/qemu-devel/2016-05/msg01196.html
