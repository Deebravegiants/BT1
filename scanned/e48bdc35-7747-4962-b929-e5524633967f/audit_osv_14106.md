# [C] CVE-2018-7225

## Summary
Severity: Critical
Advisory: CVE-2018-7225
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-02-19
Source: https://osv.dev/vulnerability/CVE-2018-7225
Type: osv

## Details
An issue was discovered in LibVNCServer through 0.9.11. rfbProcessClientNormalMessage() in rfbserver.c does not sanitize msg.cct.length, leading to access to uninitialized and potentially sensitive data or possibly unspecified other impact (e.g., an integer overflow) via specially crafted VNC packets.

## References
- https://lists.debian.org/debian-lts-announce/2019/10/msg00042.html
- https://lists.debian.org/debian-lts-announce/2019/11/msg00032.html
- https://lists.debian.org/debian-lts-announce/2019/12/msg00028.html
- https://usn.ubuntu.com/4547-1/
- https://usn.ubuntu.com/4573-1/
- https://usn.ubuntu.com/4587-1/
- http://www.securityfocus.com/bid/103107
- https://access.redhat.com/errata/RHSA-2018:1055
- https://github.com/LibVNC/libvncserver/issues/218
- https://lists.debian.org/debian-lts-announce/2018/03/msg00035.html
- https://security.gentoo.org/glsa/201908-05
- https://usn.ubuntu.com/3618-1/
- https://www.debian.org/security/2018/dsa-4221
- http://www.openwall.com/lists/oss-security/2018/02/18/1
