# [H] CVE-2019-9924

## Summary
Severity: High
Advisory: CVE-2019-9924
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-03-22
Source: https://osv.dev/vulnerability/CVE-2019-9924
Type: osv

## Details
rbash in Bash before 4.4-beta2 did not prevent the shell user from modifying BASH_CMDS, thus allowing the user to execute any command with the permissions of the shell.

## References
- http://git.savannah.gnu.org/cgit/bash.git/tree/CHANGES?h=bash-4.4-testing#n65
- http://lists.opensuse.org/opensuse-security-announce/2019-04/msg00049.html
- https://lists.debian.org/debian-lts-announce/2019/03/msg00028.html
- https://security.netapp.com/advisory/ntap-20190411-0001/
- https://usn.ubuntu.com/4058-1/
- https://usn.ubuntu.com/4058-2/
- https://bugs.launchpad.net/ubuntu/+source/bash/+bug/1803441
