# [H] CVE-2017-5618

## Summary
Severity: High
Advisory: CVE-2017-5618
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-03-20
Source: https://osv.dev/vulnerability/CVE-2017-5618
Type: osv

## Details
GNU screen before 4.5.1 allows local users to modify arbitrary files and consequently gain root privileges by leveraging improper checking of logfile permissions.

## References
- http://www.securityfocus.com/bid/95873
- http://git.savannah.gnu.org/cgit/screen.git/tree/src/ChangeLog?h=v.4.5.1
- http://savannah.gnu.org/bugs/?50142
- http://git.savannah.gnu.org/cgit/screen.git/patch/?id=1c6d2817926d30c9a7a97d99af7ac5de4a5845b8
- http://www.openwall.com/lists/oss-security/2017/01/29/3
- https://lists.gnu.org/archive/html/screen-devel/2017-01/msg00025.html
