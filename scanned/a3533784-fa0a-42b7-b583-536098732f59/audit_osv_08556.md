# [H] CVE-2016-4414

## Summary
Severity: High
Advisory: CVE-2016-4414
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-06-13
Source: https://osv.dev/vulnerability/CVE-2016-4414
Type: osv

## Details
The onReadyRead function in core/coreauthhandler.cpp in Quassel before 0.12.4 allows remote attackers to cause a denial of service (NULL pointer dereference and crash) via invalid handshake data.

## References
- http://lists.fedoraproject.org/pipermail/package-announce/2016-May/183571.html
- http://lists.fedoraproject.org/pipermail/package-announce/2016-May/183585.html
- http://lists.fedoraproject.org/pipermail/package-announce/2016-May/183746.html
- http://lists.opensuse.org/opensuse-updates/2016-05/msg00063.html
- http://quassel-irc.org/node/129
- http://www.openwall.com/lists/oss-security/2016/04/30/2
- http://www.openwall.com/lists/oss-security/2016/04/30/4
- https://github.com/quassel/quassel/commit/e678873
