# [H] CVE-2015-6855

## Summary
Severity: High
Advisory: CVE-2015-6855
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2015-11-06
Source: https://osv.dev/vulnerability/CVE-2015-6855
Type: osv

## Details
hw/ide/core.c in QEMU does not properly restrict the commands accepted by an ATAPI device, which allows guest users to cause a denial of service or possibly have unspecified other impact via certain IDE commands, as demonstrated by a WIN_READ_NATIVE_MAX command to an empty drive, which triggers a divide-by-zero error and instance crash.

## References
- http://lists.fedoraproject.org/pipermail/package-announce/2015-October/168602.html
- http://lists.fedoraproject.org/pipermail/package-announce/2015-October/169036.html
- http://lists.fedoraproject.org/pipermail/package-announce/2015-October/169039.html
- http://lists.fedoraproject.org/pipermail/package-announce/2015-October/169327.html
- http://lists.fedoraproject.org/pipermail/package-announce/2015-October/169341.html
- http://lists.fedoraproject.org/pipermail/package-announce/2015-September/167369.html
- http://lists.opensuse.org/opensuse-security-announce/2015-10/msg00019.html
- http://www.debian.org/security/2015/dsa-3361
- http://www.debian.org/security/2015/dsa-3362
- http://www.openwall.com/lists/oss-security/2015/09/10/1
- http://www.openwall.com/lists/oss-security/2015/09/10/2
- http://www.securityfocus.com/bid/76691
- http://www.ubuntu.com/usn/USN-2745-1
- https://lists.gnu.org/archive/html/qemu-devel/2015-09/msg02479.html
- https://security.gentoo.org/glsa/201602-01
- https://www.arista.com/en/support/advisories-notices/security-advisories/1188-security-advisory-14
- http://lists.opensuse.org/opensuse-security-announce/2015-10/msg00019.html
- http://www.openwall.com/lists/oss-security/2015/09/10/1
- http://www.openwall.com/lists/oss-security/2015/09/10/2
- https://lists.gnu.org/archive/html/qemu-devel/2015-09/msg02479.html
