# [M] CVE-2016-8616

## Summary
Severity: Medium
Advisory: CVE-2016-8616
Aliases: CURL-CVE-2016-8616
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2018-08-01
Source: https://osv.dev/vulnerability/CVE-2016-8616
Type: osv

## Details
A flaw was found in curl before version 7.51.0 When re-using a connection, curl was doing case insensitive comparisons of user name and password with the existing connections. This means that if an unused connection with proper credentials exists for a protocol that has connection-scoped credentials, an attacker can cause that connection to be reused if s/he knows the case-insensitive version of the correct password.

## References
- http://www.securityfocus.com/bid/94094
- http://www.securitytracker.com/id/1037192
- https://access.redhat.com/errata/RHSA-2018:2486
- https://access.redhat.com/errata/RHSA-2018:3558
- https://security.gentoo.org/glsa/201701-47
- https://www.tenable.com/security/tns-2016-21
- http://www.oracle.com/technetwork/security-advisory/cpuoct2018-4428296.html
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2016-8616
- https://curl.haxx.se/CVE-2016-8616.patch
- https://curl.haxx.se/docs/adv_20161102B.html
