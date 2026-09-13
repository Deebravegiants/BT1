# [M] CVE-2016-1897

## Summary
Severity: Medium
Advisory: CVE-2016-1897
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2016-01-15
Source: https://osv.dev/vulnerability/CVE-2016-1897
Type: osv

## Details
FFmpeg 2.x allows remote attackers to conduct cross-origin attacks and read arbitrary files by using the concat protocol in an HTTP Live Streaming (HLS) M3U8 file, leading to an external HTTP request in which the URL string contains the first line of a local file.

## References
- http://lists.opensuse.org/opensuse-security-announce/2016-01/msg00034.html
- http://www.openwall.com/lists/oss-security/2016/01/14/1
- http://www.securityfocus.com/bid/80501
- http://www.securitytracker.com/id/1034932
- http://www.slackware.com/security/viewer.php?l=slackware-security&y=2016&m=slackware-security.529036
- https://www.kb.cert.org/vuls/id/772447
- http://www.debian.org/security/2016/dsa-3506
- http://www.ubuntu.com/usn/USN-2944-1
- https://security.gentoo.org/glsa/201606-09
- https://security.gentoo.org/glsa/201705-08
- http://habrahabr.ru/company/mailru/blog/274855
- http://security.stackexchange.com/questions/110644
