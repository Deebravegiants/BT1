# [M] CVE-2019-9947

## Summary
Severity: Medium
Advisory: CVE-2019-9947
Aliases: PSF-2019-11
CVSS: 6.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N)
Published: 2019-03-23
Source: https://osv.dev/vulnerability/CVE-2019-9947
Type: osv

## Details
An issue was discovered in urllib2 in Python 2.x through 2.7.16 and urllib in Python 3.x through 3.7.3. CRLF injection is possible if the attacker controls a url parameter, as demonstrated by the first argument to urllib.request.urlopen with \r\n (specifically in the path component of a URL that lacks a ? character) followed by an HTTP header or a Redis command. This is similar to the CVE-2019-9740 query string issue. This is fixed in: v2.7.17, v2.7.17rc1, v2.7.18, v2.7.18rc1; v3.5.10, v3.5.10rc1, v3.5.8, v3.5.8rc1, v3.5.8rc2, v3.5.9; v3.6.10, v3.6.10rc1, v3.6.11, v3.6.11rc1, v3.6.12, v3.6.9, v3.6.9rc1; v3.7.4, v3.7.4rc1, v3.7.4rc2, v3.7.5, v3.7.5rc1, v3.7.6, v3.7.6rc1, v3.7.7, v3.7.7rc1, v3.7.8, v3.7.8rc1, v3.7.9.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/JMWSKTNOHSUOT3L25QFJAVCFYZX46FYK/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/JXASHCDD4PQFKTMKQN4YOP5ZH366ABN4/
- http://lists.opensuse.org/opensuse-security-announce/2019-10/msg00062.html
- http://lists.opensuse.org/opensuse-security-announce/2019-10/msg00063.html
- http://lists.opensuse.org/opensuse-security-announce/2020-01/msg00040.html
- http://www.openwall.com/lists/oss-security/2021/02/04/2
- https://access.redhat.com/errata/RHSA-2019:1260
- https://access.redhat.com/errata/RHSA-2019:2030
- https://access.redhat.com/errata/RHSA-2019:3335
- https://access.redhat.com/errata/RHSA-2019:3520
- https://access.redhat.com/errata/RHSA-2019:3725
- https://lists.debian.org/debian-lts-announce/2019/06/msg00022.html
- https://lists.debian.org/debian-lts-announce/2019/06/msg00023.html
- https://lists.debian.org/debian-lts-announce/2019/06/msg00026.html
- https://lists.debian.org/debian-lts-announce/2020/07/msg00011.html
- https://lists.debian.org/debian-lts-announce/2020/08/msg00034.html
- https://security.gentoo.org/glsa/202003-26
- https://security.netapp.com/advisory/ntap-20190404-0004/
- https://usn.ubuntu.com/4127-1/
- https://usn.ubuntu.com/4127-2/
