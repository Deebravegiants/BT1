# [C] CVE-2015-8972

## Summary
Severity: Critical
Advisory: CVE-2015-8972
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-01-23
Source: https://osv.dev/vulnerability/CVE-2015-8972
Type: osv

## Details
Stack-based buffer overflow in the ValidateMove function in frontend/move.cc in GNU Chess (aka gnuchess) before 6.2.4 might allow context-dependent attackers to execute arbitrary code via a large input, as demonstrated when in UCI mode.

## References
- http://lists.gnu.org/archive/html/bug-gnu-chess/2015-10/msg00002.html
- http://svn.savannah.gnu.org/viewvc/chess?revision=134&view=revision
- http://www.openwall.com/lists/oss-security/2016/11/13/2
- http://www.openwall.com/lists/oss-security/2016/11/14/11
- http://www.openwall.com/lists/oss-security/2016/11/14/12
- http://www.openwall.com/lists/oss-security/2016/11/13/2
- http://www.openwall.com/lists/oss-security/2016/11/14/11
- http://www.openwall.com/lists/oss-security/2016/11/14/12
- http://lists.gnu.org/archive/html/bug-gnu-chess/2015-10/msg00002.html
- http://svn.savannah.gnu.org/viewvc/chess?revision=134&view=revision
