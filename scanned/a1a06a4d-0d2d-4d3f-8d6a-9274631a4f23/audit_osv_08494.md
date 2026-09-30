# [H] CVE-2016-3947

## Summary
Severity: High
Advisory: CVE-2016-3947
CVSS: 8.2 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:H)
Published: 2016-04-07
Source: https://osv.dev/vulnerability/CVE-2016-3947
Type: osv

## Details
Heap-based buffer overflow in the Icmp6::Recv function in icmp/Icmp6.cc in the pinger utility in Squid before 3.5.16 and 4.x before 4.0.8 allows remote servers to cause a denial of service (performance degradation or transition failures) or write sensitive information to log files via an ICMPv6 packet.

## References
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00010.html
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00040.html
- http://lists.opensuse.org/opensuse-updates/2016-08/msg00069.html
- http://www.securitytracker.com/id/1035457
- http://www.squid-cache.org/Advisories/SQUID-2016_3.txt
- http://www.ubuntu.com/usn/USN-2995-1
- https://security.gentoo.org/glsa/201607-01
- http://www.squid-cache.org/Versions/v3/3.1/changesets/squid-3.1-10495.patch
- http://www.squid-cache.org/Versions/v3/3.2/changesets/squid-3.2-11839.patch
- http://www.squid-cache.org/Versions/v3/3.3/changesets/squid-3.3-12694.patch
- http://www.squid-cache.org/Versions/v3/3.4/changesets/squid-3.4-13232.patch
- http://www.squid-cache.org/Versions/v3/3.5/changesets/squid-3.5-14015.patch
