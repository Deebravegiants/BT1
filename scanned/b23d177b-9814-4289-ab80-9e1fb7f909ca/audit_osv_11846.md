# [M] CVE-2018-0494

## Summary
Severity: Medium
Advisory: CVE-2018-0494
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N)
Published: 2018-05-06
Source: https://osv.dev/vulnerability/CVE-2018-0494
Type: osv

## Details
GNU Wget before 1.19.5 is prone to a cookie injection vulnerability in the resp_new function in http.c via a \r\n sequence in a continuation line.

## References
- https://savannah.gnu.org/bugs/?53763
- http://www.securityfocus.com/bid/104129
- http://www.securitytracker.com/id/1040838
- https://access.redhat.com/errata/RHSA-2018:3052
- https://git.savannah.gnu.org/cgit/wget.git/commit/?id=1fc9c95ec144499e69dc8ec76dbe07799d7d82cd
- https://lists.debian.org/debian-lts-announce/2018/05/msg00006.html
- https://security.gentoo.org/glsa/201806-01
- https://usn.ubuntu.com/3643-1/
- https://usn.ubuntu.com/3643-2/
- https://www.debian.org/security/2018/dsa-4195
- https://lists.gnu.org/archive/html/bug-wget/2018-05/msg00020.html
- https://sintonen.fi/advisories/gnu-wget-cookie-injection.txt
- https://www.exploit-db.com/exploits/44601/
