# [M] CVE-2016-1922

## Summary
Severity: Medium
Advisory: CVE-2016-1922
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-12-29
Source: https://osv.dev/vulnerability/CVE-2016-1922
Type: osv

## Details
QEMU (aka Quick Emulator) built with the TPR optimization for 32-bit Windows guests support is vulnerable to a null pointer dereference flaw. It occurs while doing I/O port write operations via hmp interface. In that, 'current_cpu' remains null, which leads to the null pointer dereference. A user or process could use this flaw to crash the QEMU instance, resulting in DoS issue.

## References
- http://www.debian.org/security/2016/dsa-3469
- http://www.debian.org/security/2016/dsa-3470
- http://www.debian.org/security/2016/dsa-3471
- http://www.openwall.com/lists/oss-security/2016/01/16/1
- http://www.openwall.com/lists/oss-security/2016/01/16/6
- http://www.securityfocus.com/bid/81058
- https://security.gentoo.org/glsa/201604-01
- https://bugzilla.redhat.com/show_bug.cgi?id=1283934
- https://lists.gnu.org/archive/html/qemu-devel/2016-01/msg02812.html
