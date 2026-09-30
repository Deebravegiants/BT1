# [H] CVE-2016-4553

## Summary
Severity: High
Advisory: CVE-2016-4553
CVSS: 8.6 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:C/C:N/I:H/A:N)
Published: 2016-05-10
Source: https://osv.dev/vulnerability/CVE-2016-4553
Type: osv

## Details
client_side.cc in Squid before 3.5.18 and 4.x before 4.0.10 does not properly ignore the Host header when absolute-URI is provided, which allows remote attackers to conduct cache-poisoning attacks via an HTTP request.

## References
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00010.html
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00040.html
- http://lists.opensuse.org/opensuse-updates/2016-08/msg00069.html
- http://www.squid-cache.org/Versions/v3/3.5/changesets/squid-3.5-14039.patch
- http://bugs.squid-cache.org/show_bug.cgi?id=4501
- http://www.debian.org/security/2016/dsa-3625
- http://www.oracle.com/technetwork/topics/security/linuxbulletinapr2016-2952096.html
- http://www.securitytracker.com/id/1035768
- http://www.squid-cache.org/Advisories/SQUID-2016_7.txt
- http://www.ubuntu.com/usn/USN-2995-1
- https://access.redhat.com/errata/RHSA-2016:1139
- https://access.redhat.com/errata/RHSA-2016:1140
- https://security.gentoo.org/glsa/201607-01
