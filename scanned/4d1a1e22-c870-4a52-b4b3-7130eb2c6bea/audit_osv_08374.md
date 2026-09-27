# [H] CVE-2016-2570

## Summary
Severity: High
Advisory: CVE-2016-2570
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-02-27
Source: https://osv.dev/vulnerability/CVE-2016-2570
Type: osv

## Details
The Edge Side Includes (ESI) parser in Squid 3.x before 3.5.15 and 4.x before 4.0.7 does not check buffer limits during XML parsing, which allows remote HTTP servers to cause a denial of service (assertion failure and daemon exit) via a crafted XML document, related to esi/CustomParser.cc and esi/CustomParser.h.

## References
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00010.html
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00040.html
- http://lists.opensuse.org/opensuse-updates/2016-08/msg00069.html
- http://www.openwall.com/lists/oss-security/2016/02/26/2
- http://www.securitytracker.com/id/1035101
- http://www.squid-cache.org/Versions/v3/3.5/changesets/squid-3.5-13993.patch
- http://www.squid-cache.org/Versions/v4/changesets/squid-4-14549.patch
- https://usn.ubuntu.com/3557-1/
- http://rhn.redhat.com/errata/RHSA-2016-2600.html
- http://www.squid-cache.org/Advisories/SQUID-2016_2.txt
- https://security.gentoo.org/glsa/201607-01
