# [H] CVE-2016-8659

## Summary
Severity: High
Advisory: CVE-2016-8659
CVSS: 7.0 (CVSS:3.0/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-02-13
Source: https://osv.dev/vulnerability/CVE-2016-8659
Type: osv

## Details
Bubblewrap before 0.1.3 sets the PR_SET_DUMPABLE flag, which might allow local users to gain privileges by attaching to the process, as demonstrated by sending commands to a PrivSep socket.

## References
- http://www.openwall.com/lists/oss-security/2016/10/12/5
- http://www.securityfocus.com/bid/93542
- http://www.openwall.com/lists/oss-security/2016/10/13/4
- https://github.com/projectatomic/bubblewrap/issues/107
