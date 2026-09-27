# [H] CVE-2016-2568

## Summary
Severity: High
Advisory: CVE-2016-2568
CVSS: 7.8 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2017-02-13
Source: https://osv.dev/vulnerability/CVE-2016-2568
Type: osv

## Details
pkexec, when used with --user nonpriv, allows local users to escape to the parent session via a crafted TIOCSTI ioctl call, which pushes characters to the terminal's input buffer.

## References
- http://www.openwall.com/lists/oss-security/2016/02/26/3
- https://access.redhat.com/security/cve/cve-2016-2568
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=816062
- https://ubuntu.com/security/CVE-2016-2568
- https://bugzilla.redhat.com/show_bug.cgi?id=1300746
