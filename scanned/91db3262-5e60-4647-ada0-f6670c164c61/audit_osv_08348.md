# [M] CVE-2016-2390

## Summary
Severity: Medium
Advisory: CVE-2016-2390
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-04-19
Source: https://osv.dev/vulnerability/CVE-2016-2390
Type: osv

## Details
The FwdState::connectedToPeer method in FwdState.cc in Squid before 3.5.14 and 4.0.x before 4.0.6 does not properly handle SSL handshake errors when built with the --with-openssl option, which allows remote attackers to cause a denial of service (application crash) via a plaintext HTTP message.

## References
- http://bugs.squid-cache.org/show_bug.cgi?id=4437
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00010.html
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00040.html
- http://www.securitytracker.com/id/1035045
- http://lists.squid-cache.org/pipermail/squid-announce/2016-February/000037.html
- http://lists.squid-cache.org/pipermail/squid-announce/2016-February/000038.html
- http://www.squid-cache.org/Advisories/SQUID-2016_1.txt
