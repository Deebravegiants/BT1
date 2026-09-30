# [H] CVE-2016-2779

## Summary
Severity: High
Advisory: CVE-2016-2779
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-02-07
Source: https://osv.dev/vulnerability/CVE-2016-2779
Type: osv

## Details
runuser in util-linux allows local users to escape to the parent session via a crafted TIOCSTI ioctl call, which pushes characters to the terminal's input buffer.

## References
- http://www.openwall.com/lists/oss-security/2016/02/27/2
- http://www.openwall.com/lists/oss-security/2016/02/27/1
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=815922
