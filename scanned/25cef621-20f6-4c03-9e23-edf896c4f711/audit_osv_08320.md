# [M] CVE-2016-2197

## Summary
Severity: Medium
Advisory: CVE-2016-2197
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-12-29
Source: https://osv.dev/vulnerability/CVE-2016-2197
Type: osv

## Details
QEMU (aka Quick Emulator) built with an IDE AHCI emulation support is vulnerable to a null pointer dereference flaw. It occurs while unmapping the Frame Information Structure (FIS) and Command List Block (CLB) entries. A privileged user inside guest could use this flaw to crash the QEMU process instance resulting in DoS.

## References
- http://www.openwall.com/lists/oss-security/2016/01/29/2
- http://www.openwall.com/lists/oss-security/2016/01/30/1
- http://www.securityfocus.com/bid/82235
- https://security.gentoo.org/glsa/201604-01
- https://bugzilla.redhat.com/show_bug.cgi?id=1302057
- https://lists.gnu.org/archive/html/qemu-devel/2016-01/msg05742.html
