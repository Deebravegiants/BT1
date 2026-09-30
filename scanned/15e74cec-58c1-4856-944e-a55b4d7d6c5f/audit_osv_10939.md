# [C] CVE-2017-5226

## Summary
Severity: Critical
Advisory: CVE-2017-5226
CVSS: 10.0 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2017-03-29
Source: https://osv.dev/vulnerability/CVE-2017-5226
Type: osv

## Details
When executing a program via the bubblewrap sandbox, the nonpriv session can escape to the parent session by using the TIOCSTI ioctl to push characters into the terminal's input buffer, allowing an attacker to escape the sandbox.

## References
- http://www.openwall.com/lists/oss-security/2020/07/10/1
- http://www.openwall.com/lists/oss-security/2023/03/17/1
- https://www.openwall.com/lists/oss-security/2023/03/14/2
- http://www.securityfocus.com/bid/97260
- https://bugzilla.redhat.com/show_bug.cgi?id=1411811
- https://github.com/projectatomic/bubblewrap/commit/d7fc532c42f0e9bf427923bab85433282b3e5117
- https://github.com/projectatomic/bubblewrap/issues/142
