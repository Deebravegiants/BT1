# [M] CVE-2015-8701

## Summary
Severity: Medium
Advisory: CVE-2015-8701
CVSS: 6.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2016-12-29
Source: https://osv.dev/vulnerability/CVE-2015-8701
Type: osv

## Details
QEMU (aka Quick Emulator) built with the Rocker switch emulation support is vulnerable to an off-by-one error. It happens while processing transmit (tx) descriptors in 'tx_consume' routine, if a descriptor was to have more than allowed (ROCKER_TX_FRAGS_MAX=16) fragments. A privileged user inside guest could use this flaw to cause memory leakage on the host or crash the QEMU process instance resulting in DoS issue.

## References
- http://www.openwall.com/lists/oss-security/2015/12/28/6
- http://www.openwall.com/lists/oss-security/2015/12/29/1
- http://www.securityfocus.com/bid/79706
- https://lists.gnu.org/archive/html/qemu-devel/2015-12/msg04629.html
- https://security.gentoo.org/glsa/201602-01
- http://www.openwall.com/lists/oss-security/2015/12/28/6
- http://www.openwall.com/lists/oss-security/2015/12/29/1
- https://lists.gnu.org/archive/html/qemu-devel/2015-12/msg04629.html
- https://bugzilla.redhat.com/show_bug.cgi?id=1286971
