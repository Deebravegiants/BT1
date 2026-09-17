# [C] CVE-2020-13753

## Summary
Severity: Critical
Advisory: CVE-2020-13753
CVSS: 10.0 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2020-07-14
Source: https://osv.dev/vulnerability/CVE-2020-13753
Type: osv

## Details
The bubblewrap sandbox of WebKitGTK and WPE WebKit, prior to 2.28.3, failed to properly block access to CLONE_NEWUSER and the TIOCSTI ioctl. CLONE_NEWUSER could potentially be used to confuse xdg-desktop-portal, which allows access outside the sandbox. TIOCSTI can be used to directly execute commands outside the sandbox by writing to the controlling terminal's input buffer, similar to CVE-2017-5226.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/GER2ATKZXDHM7FFYJH67ZPNZZX5VOUVM/
- https://security.gentoo.org/glsa/202007-11
- https://usn.ubuntu.com/4422-1/
- https://www.debian.org/security/2020/dsa-4724
- https://www.openwall.com/lists/oss-security/2020/07/10/1
- http://lists.opensuse.org/opensuse-security-announce/2020-07/msg00074.html
- https://trac.webkit.org/changeset/262368/webkit
