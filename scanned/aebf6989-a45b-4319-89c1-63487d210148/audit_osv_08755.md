# [M] CVE-2016-5699

## Summary
Severity: Medium
Advisory: CVE-2016-5699
Aliases: PSF-2016-8
CVSS: 6.1 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N)
Published: 2016-09-02
Source: https://osv.dev/vulnerability/CVE-2016-5699
Type: osv

## Details
CRLF injection vulnerability in the HTTPConnection.putheader function in urllib2 and urllib in CPython (aka Python) before 2.7.10 and 3.x before 3.4.4 allows remote attackers to inject arbitrary HTTP headers via CRLF sequences in a URL.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-01/msg00040.html
- http://www.oracle.com/technetwork/topics/security/bulletinjul2016-3090568.html
- http://www.securityfocus.com/bid/91226
- http://www.splunk.com/view/SP-CAAAPSV
- http://www.splunk.com/view/SP-CAAAPUE
- https://lists.debian.org/debian-lts-announce/2019/02/msg00011.html
- http://rhn.redhat.com/errata/RHSA-2016-1626.html
- http://rhn.redhat.com/errata/RHSA-2016-1627.html
- http://rhn.redhat.com/errata/RHSA-2016-1628.html
- http://rhn.redhat.com/errata/RHSA-2016-1629.html
- http://rhn.redhat.com/errata/RHSA-2016-1630.html
- https://docs.python.org/3.4/whatsnew/changelog.html#python-3-4-4
- https://hg.python.org/cpython/raw-file/v2.7.10/Misc/NEWS
- https://hg.python.org/cpython/rev/1c45047c5102
- https://hg.python.org/cpython/rev/bf3e1c9b80e9
- http://www.openwall.com/lists/oss-security/2016/06/14/7
- http://www.openwall.com/lists/oss-security/2016/06/15/12
- http://www.openwall.com/lists/oss-security/2016/06/16/2
- http://blog.blindspotsecurity.com/2016/06/advisory-http-header-injection-in.html
