# [H] CVE-2016-1954

## Summary
Severity: High
Advisory: CVE-2016-1954
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2016-03-13
Source: https://osv.dev/vulnerability/CVE-2016-1954
Type: osv

## Details
The nsCSPContext::SendReports function in dom/security/nsCSPContext.cpp in Mozilla Firefox before 45.0 and Firefox ESR 38.x before 38.7 does not prevent use of a non-HTTP report-uri for a Content Security Policy (CSP) violation report, which allows remote attackers to cause a denial of service (data overwrite) or possibly gain privileges by specifying a URL of a local file.

## References
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00027.html
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00050.html
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00089.html
- http://www.securitytracker.com/id/1035215
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00068.html
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00029.html
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00031.html
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00093.html
- http://www.mozilla.org/security/announce/2016/mfsa2016-17.html
- http://www.ubuntu.com/usn/USN-2917-3
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00091.html
- http://lists.opensuse.org/opensuse-security-announce/2016-07/msg00006.html
- http://lists.opensuse.org/opensuse-security-announce/2016-07/msg00008.html
- https://security.gentoo.org/glsa/201605-06
- http://www.oracle.com/technetwork/topics/security/linuxbulletinjan2016-2867209.html
- http://www.ubuntu.com/usn/USN-2917-2
- http://www.ubuntu.com/usn/USN-2917-1
- http://www.ubuntu.com/usn/USN-2934-1
- http://lists.opensuse.org/opensuse-security-announce/2016-07/msg00007.html
- http://www.debian.org/security/2016/dsa-3510
