# [M] CVE-2015-5239

## Summary
Severity: Medium
Advisory: CVE-2015-5239
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-01-23
Source: https://osv.dev/vulnerability/CVE-2015-5239
Type: osv

## Details
Integer overflow in the VNC display driver in QEMU before 2.1.0 allows attachers to cause a denial of service (process crash) via a CLIENT_CUT_TEXT message, which triggers an infinite loop.

## References
- http://lists.fedoraproject.org/pipermail/package-announce/2015-October/168077.html
- http://lists.fedoraproject.org/pipermail/package-announce/2015-October/168646.html
- http://lists.fedoraproject.org/pipermail/package-announce/2015-October/168671.html
- http://lists.opensuse.org/opensuse-security-announce/2015-10/msg00026.html
- http://lists.opensuse.org/opensuse-security-announce/2015-11/msg00005.html
- http://lists.opensuse.org/opensuse-security-announce/2015-11/msg00011.html
- http://www.openwall.com/lists/oss-security/2015/09/02/7
- http://www.ubuntu.com/usn/USN-2745-1
- https://github.com/qemu/qemu/commit/f9a70e79391f6d7c2a912d785239ee8effc1922d
- https://www.arista.com/en/support/advisories-notices/security-advisories/1188-security-advisory-14
- http://lists.fedoraproject.org/pipermail/package-announce/2015-October/168077.html
- http://lists.fedoraproject.org/pipermail/package-announce/2015-October/168646.html
- http://lists.fedoraproject.org/pipermail/package-announce/2015-October/168671.html
- http://lists.opensuse.org/opensuse-security-announce/2015-10/msg00026.html
- http://lists.opensuse.org/opensuse-security-announce/2015-11/msg00005.html
- http://lists.opensuse.org/opensuse-security-announce/2015-11/msg00011.html
- http://www.openwall.com/lists/oss-security/2015/09/02/7
- http://www.openwall.com/lists/oss-security/2015/09/02/7
- http://www.ubuntu.com/usn/USN-2745-1
- https://github.com/qemu/qemu/commit/f9a70e79391f6d7c2a912d785239ee8effc1922d
