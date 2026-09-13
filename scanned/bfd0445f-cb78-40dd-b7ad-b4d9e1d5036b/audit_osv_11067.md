# [H] CVE-2017-5932

## Summary
Severity: High
Advisory: CVE-2017-5932
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-03-27
Source: https://osv.dev/vulnerability/CVE-2017-5932
Type: osv

## Details
The path autocompletion feature in Bash 4.4 allows local users to gain privileges via a crafted filename starting with a " (double quote) character and a command substitution metacharacter.

## References
- http://www.securityfocus.com/bid/96136
- http://git.savannah.gnu.org/cgit/bash.git/commit/?id=4f747edc625815f449048579f6e65869914dd715
- http://www.openwall.com/lists/oss-security/2017/02/08/3
- https://lists.gnu.org/archive/html/bug-bash/2017-01/msg00034.html
