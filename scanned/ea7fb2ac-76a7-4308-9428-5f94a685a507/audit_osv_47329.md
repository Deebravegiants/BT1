# [M] CVE-2016-2781

## Summary
Severity: Medium
Advisory: CVE-2016-2781
CVSS: 6.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:C/C:N/I:H/A:N)
Published: 2017-02-07
Source: https://osv.dev/vulnerability/CVE-2016-2781
Type: osv

## Details
chroot in GNU coreutils, when used with --userspec, allows local users to escape to the parent session via a crafted TIOCSTI ioctl call, which pushes characters to the terminal's input buffer.

## References
- https://lists.apache.org/thread.html/rf9fa47ab66495c78bb4120b0754dd9531ca2ff0430f6685ac9b07772%40%3Cdev.mina.apache.org%3E
- http://www.openwall.com/lists/oss-security/2016/02/28/2
- http://www.openwall.com/lists/oss-security/2016/02/28/3
