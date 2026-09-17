# [M] CVE-2016-1981

## Summary
Severity: Medium
Advisory: CVE-2016-1981
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-12-29
Source: https://osv.dev/vulnerability/CVE-2016-1981
Type: osv

## Details
QEMU (aka Quick Emulator) built with the e1000 NIC emulation support is vulnerable to an infinite loop issue. It could occur while processing data via transmit or receive descriptors, provided the initial receive/transmit descriptor head (TDH/RDH) is set outside the allocated descriptor buffer. A privileged user inside guest could use this flaw to crash the QEMU instance resulting in DoS.

## References
- http://rhn.redhat.com/errata/RHSA-2016-2585.html
- http://www.debian.org/security/2016/dsa-3469
- http://www.debian.org/security/2016/dsa-3470
- http://www.debian.org/security/2016/dsa-3471
- http://www.openwall.com/lists/oss-security/2016/01/19/10
- http://www.openwall.com/lists/oss-security/2016/01/22/1
- http://www.securityfocus.com/bid/81549
- https://security.gentoo.org/glsa/201604-01
- https://bugzilla.redhat.com/show_bug.cgi?id=1298570
- https://lists.gnu.org/archive/html/qemu-devel/2016-01/msg03454.html
