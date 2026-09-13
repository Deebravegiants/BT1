# [M] CVE-2017-8806

## Summary
Severity: Medium
Advisory: CVE-2017-8806
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2017-11-13
Source: https://osv.dev/vulnerability/CVE-2017-8806
Type: osv

## Details
The Debian pg_ctlcluster, pg_createcluster, and pg_upgradecluster scripts, as distributed in the Debian postgresql-common package before 181+deb9u1 for PostgreSQL (and other packages related to Debian and Ubuntu), handled symbolic links insecurely, which could result in local denial of service by overwriting arbitrary files.

## References
- http://metadata.ftp-master.debian.org/changelogs/main/p/postgresql-common/postgresql-common_181+deb9u1_changelog
- http://www.securityfocus.com/bid/101810
- https://usn.ubuntu.com/usn/usn-3476-1/
- https://www.debian.org/security/2017/dsa-4029
- http://metadata.ftp-master.debian.org/changelogs/main/p/postgresql-common/postgresql-common_181+deb9u1_changelog
- https://usn.ubuntu.com/usn/usn-3476-1/
- https://www.debian.org/security/2017/dsa-4029
- http://metadata.ftp-master.debian.org/changelogs/main/p/postgresql-common/postgresql-common_181+deb9u1_changelog
- http://www.securityfocus.com/bid/101810
