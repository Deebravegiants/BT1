# [M] CVE-2017-17087

## Summary
Severity: Medium
Advisory: CVE-2017-17087
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2017-12-01
Source: https://osv.dev/vulnerability/CVE-2017-17087
Type: osv

## Details
fileio.c in Vim prior to 8.0.1263 sets the group ownership of a .swp file to the editor's primary group (which may be different from the group ownership of the original file), which allows local users to obtain sensitive information by leveraging an applicable group membership, as demonstrated by /etc/shadow owned by root:shadow mode 0640, but /etc/.shadow.swp owned by root:users mode 0640, a different vulnerability than CVE-2017-1000382.

## References
- https://lists.debian.org/debian-lts-announce/2019/08/msg00003.html
- https://lists.debian.org/debian-lts-announce/2022/01/msg00003.html
- https://usn.ubuntu.com/4582-1/
- http://security.cucumberlinux.com/security/details.php?id=166
- https://groups.google.com/d/msg/vim_dev/sRT9BtjLWMk/BRtSXNU4BwAJ
- https://github.com/vim/vim/commit/5a73e0ca54c77e067c3b12ea6f35e3e8681e8cf8
- http://openwall.com/lists/oss-security/2017/11/27/2
