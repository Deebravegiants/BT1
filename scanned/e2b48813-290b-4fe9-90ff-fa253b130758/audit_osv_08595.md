# [H] CVE-2016-4554

## Summary
Severity: High
Advisory: CVE-2016-4554
CVSS: 8.6 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:C/C:N/I:H/A:N)
Published: 2016-05-10
Source: https://osv.dev/vulnerability/CVE-2016-4554
Type: osv

## Details
mime_header.cc in Squid before 3.5.18 allows remote attackers to bypass intended same-origin restrictions and possibly conduct cache-poisoning attacks via a crafted HTTP Host header, aka a "header smuggling" issue.

## References
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00010.html
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00040.html
- http://lists.opensuse.org/opensuse-updates/2016-08/msg00069.html
- http://www.debian.org/security/2016/dsa-3625
- http://www.oracle.com/technetwork/topics/security/linuxbulletinapr2016-2952096.html
- http://www.securitytracker.com/id/1035769
- http://www.squid-cache.org/Advisories/SQUID-2016_8.txt
- http://www.ubuntu.com/usn/USN-2995-1
- https://access.redhat.com/errata/RHSA-2016:1138
- https://access.redhat.com/errata/RHSA-2016:1139
- https://access.redhat.com/errata/RHSA-2016:1140
- https://security.gentoo.org/glsa/201607-01
- http://www.squid-cache.org/Versions/v3/3.1/changesets/SQUID-2016_8.patch
- http://www.squid-cache.org/Versions/v3/3.2/changesets/SQUID-2016_8.patch
- http://www.squid-cache.org/Versions/v3/3.3/changesets/SQUID-2016_8.patch
- http://www.squid-cache.org/Versions/v3/3.4/changesets/SQUID-2016_8.patch
- http://www.squid-cache.org/Versions/v3/3.5/changesets/SQUID-2016_8.patch
