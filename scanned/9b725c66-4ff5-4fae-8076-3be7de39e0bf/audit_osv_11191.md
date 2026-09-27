# [M] CVE-2017-6508

## Summary
Severity: Medium
Advisory: CVE-2017-6508
CVSS: 6.1 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N)
Published: 2017-03-07
Source: https://osv.dev/vulnerability/CVE-2017-6508
Type: osv

## Details
CRLF injection vulnerability in the url_parse function in url.c in Wget through 1.19.1 allows remote attackers to inject arbitrary HTTP headers via CRLF sequences in the host subcomponent of a URL.

## References
- http://www.securityfocus.com/bid/96877
- https://security.gentoo.org/glsa/201706-16
- http://git.savannah.gnu.org/cgit/wget.git/commit/?id=4d729e322fae359a1aefaafec1144764a54e8ad4
- http://lists.gnu.org/archive/html/bug-wget/2017-03/msg00018.html
