# [H] CVE-2016-10124

## Summary
Severity: High
Advisory: CVE-2016-10124
CVSS: 8.6 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:C/C:N/I:H/A:N)
Published: 2017-01-09
Source: https://osv.dev/vulnerability/CVE-2016-10124
Type: osv

## Details
An issue was discovered in Linux Containers (LXC) before 2016-02-22. When executing a program via lxc-attach, the nonpriv session can escape to the parent session by using the TIOCSTI ioctl to push characters into the terminal's input buffer, allowing an attacker to escape the container.

## References
- http://www.openwall.com/lists/oss-security/2014/12/15/5
- http://www.openwall.com/lists/oss-security/2015/09/03/5
- http://www.securityfocus.com/bid/95404
- https://security.gentoo.org/glsa/201711-09
- https://github.com/lxc/lxc/commit/e986ea3dfa4a2957f71ae9bfaed406dd6e1ffff6
