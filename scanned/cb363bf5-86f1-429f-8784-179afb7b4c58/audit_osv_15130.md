# [C] CVE-2019-13640

## Summary
Severity: Critical
Advisory: CVE-2019-13640
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-07-17
Source: https://osv.dev/vulnerability/CVE-2019-13640
Type: osv

## Details
In qBittorrent before 4.1.7, the function Application::runExternalProgram() located in app/application.cpp allows command injection via shell metacharacters in the torrent name parameter or current tracker parameter, as demonstrated by remote command execution via a crafted name within an RSS feed.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-08/msg00080.html
- http://lists.opensuse.org/opensuse-security-announce/2019-08/msg00085.html
- http://www.openwall.com/lists/oss-security/2024/10/30/4
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/5T4XAX2VUI4WMAS5AI4OE3OEQSQCDCF5/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/OH3WYCKODG4OKMC4S6PWHLHAWWU6ORNC/
- https://www.debian.org/security/2020/dsa-4650
- https://github.com/qbittorrent/qBittorrent/issues/10925
