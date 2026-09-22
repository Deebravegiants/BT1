# [M] CVE-2017-7418

## Summary
Severity: Medium
Advisory: CVE-2017-7418
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2017-04-04
Source: https://osv.dev/vulnerability/CVE-2017-7418
Type: osv

## Details
ProFTPD before 1.3.5e and 1.3.6 before 1.3.6rc5 controls whether the home directory of a user could contain a symbolic link through the AllowChrootSymlinks configuration option, but checks only the last path component when enforcing AllowChrootSymlinks. Attackers with local access could bypass the AllowChrootSymlinks control by replacing a path component (other than the last one) with a symbolic link. The threat model includes an attacker who is not granted full filesystem access by a hosting provider, but can reconfigure the home directory of an FTP user.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-08/msg00004.html
- http://lists.opensuse.org/opensuse-security-announce/2019-08/msg00022.html
- http://lists.opensuse.org/opensuse-security-announce/2020-01/msg00009.html
- http://www.securityfocus.com/bid/97409
- http://bugs.proftpd.org/show_bug.cgi?id=4295
- https://github.com/proftpd/proftpd/commit/ecff21e0d0e84f35c299ef91d7fda088e516d4ed
- https://github.com/proftpd/proftpd/commit/f59593e6ff730b832dbe8754916cb5c821db579f
- https://github.com/proftpd/proftpd/pull/444/commits/349addc3be4fcdad9bd4ec01ad1ccd916c898ed8
