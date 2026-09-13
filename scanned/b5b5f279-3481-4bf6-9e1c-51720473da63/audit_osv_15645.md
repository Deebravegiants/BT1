# [M] CVE-2019-18348

## Summary
Severity: Medium
Advisory: CVE-2019-18348
Aliases: PSF-2019-7
CVSS: 6.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N)
Published: 2019-10-23
Source: https://osv.dev/vulnerability/CVE-2019-18348
Type: osv

## Details
An issue was discovered in urllib2 in Python 2.x through 2.7.17 and urllib in Python 3.x through 3.8.0. CRLF injection is possible if the attacker controls a url parameter, as demonstrated by the first argument to urllib.request.urlopen with \r\n (specifically in the host component of a URL) followed by an HTTP header. This is similar to the CVE-2019-9740 query string issue and the CVE-2019-9947 path string issue. (This is not exploitable when glibc has CVE-2016-10739 fixed.). This is fixed in: v2.7.18, v2.7.18rc1; v3.5.10, v3.5.10rc1; v3.6.11, v3.6.11rc1, v3.6.12; v3.7.8, v3.7.8rc1, v3.7.9; v3.8.3, v3.8.3rc1, v3.8.4, v3.8.4rc1, v3.8.5, v3.8.6, v3.8.6rc1.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/4X3HW5JRZ7GCPSR7UHJOLD7AWLTQCDVR/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/A5NSAX4SC3V64PGZUPH7PRDLSON34Q5A/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/JCPGLTTOBB3QEARDX4JOYURP6ELNNA2V/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/M34WOYCDKTDE5KLUACE2YIEH7D37KHRX/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/UESGYI5XDAHJBATEZN3MHNDUBDH47AS6/
- https://bugs.python.org/issue30458#msg347282
- https://bugzilla.redhat.com/show_bug.cgi?id=1727276
- http://lists.opensuse.org/opensuse-security-announce/2020-05/msg00041.html
- https://lists.debian.org/debian-lts-announce/2020/07/msg00011.html
- https://security.netapp.com/advisory/ntap-20191107-0004/
- https://usn.ubuntu.com/4333-1/
- https://usn.ubuntu.com/4333-2/
- https://www.oracle.com/security-alerts/cpuoct2020.html
