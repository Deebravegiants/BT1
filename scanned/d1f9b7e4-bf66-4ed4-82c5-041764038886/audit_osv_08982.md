# [H] CVE-2016-7141

## Summary
Severity: High
Advisory: CVE-2016-7141
Aliases: CURL-CVE-2016-7141
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2016-10-03
Source: https://osv.dev/vulnerability/CVE-2016-7141
Type: osv

## Details
curl and libcurl before 7.50.2, when built with NSS and the libnsspem.so library is available at runtime, allow remote attackers to hijack the authentication of a TLS connection by leveraging reuse of a previously loaded client certificate from file for a connection for which no certificate has been set, a different vulnerability than CVE-2016-5420.

## References
- https://lists.debian.org/debian-lts-announce/2018/11/msg00005.html
- http://lists.opensuse.org/opensuse-updates/2016-09/msg00094.html
- http://rhn.redhat.com/errata/RHSA-2016-2575.html
- http://rhn.redhat.com/errata/RHSA-2016-2957.html
- http://www.oracle.com/technetwork/security-advisory/cpuoct2018-4428296.html
- http://www.securityfocus.com/bid/92754
- http://www.securitytracker.com/id/1036739
- https://access.redhat.com/errata/RHSA-2018:3558
- https://security.gentoo.org/glsa/201701-47
- https://bugzilla.redhat.com/show_bug.cgi?id=1373229
- https://curl.haxx.se/docs/adv_20160907.html
- https://github.com/curl/curl/commit/curl-7_50_2~32
