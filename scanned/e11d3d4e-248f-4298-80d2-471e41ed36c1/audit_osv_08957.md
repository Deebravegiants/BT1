# [H] CVE-2016-7072

## Summary
Severity: High
Advisory: CVE-2016-7072
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-09-10
Source: https://osv.dev/vulnerability/CVE-2016-7072
Type: osv

## Details
An issue has been found in PowerDNS Authoritative Server before 3.4.11 and 4.0.2 allowing a remote, unauthenticated attacker to cause a denial of service by opening a large number of TCP connections to the web server. If the web server runs out of file descriptors, it triggers an exception and terminates the whole PowerDNS process. While it's more complicated for an unauthorized attacker to make the web server run out of file descriptors since its connection will be closed just after being accepted, it might still be possible.

## References
- https://doc.powerdns.com/md/security/powerdns-advisory-2016-03/
- https://www.debian.org/security/2017/dsa-3764
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2016-7072
