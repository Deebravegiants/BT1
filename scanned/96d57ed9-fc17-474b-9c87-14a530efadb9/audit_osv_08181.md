# [H] CVE-2016-1255

## Summary
Severity: High
Advisory: CVE-2016-1255
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-12-05
Source: https://osv.dev/vulnerability/CVE-2016-1255
Type: osv

## Details
The pg_ctlcluster script in postgresql-common package in Debian wheezy before 134wheezy5, in Debian jessie before 165+deb8u2, in Debian unstable before 178, in Ubuntu 12.04 LTS before 129ubuntu1.2, in Ubuntu 14.04 LTS before 154ubuntu1.1, in Ubuntu 16.04 LTS before 173ubuntu0.1, in Ubuntu 17.04 before 179ubuntu0.1, and in Ubuntu 17.10 before 184ubuntu1.1 allows local users to gain root privileges via a symlink attack on a logfile in /var/log/postgresql.

## References
- http://www.ubuntu.com/usn/USN-3476-1
- http://www.ubuntu.com/usn/USN-3476-2
- https://lists.debian.org/debian-lts-announce/2017/01/msg00002.html
- https://anonscm.debian.org/cgit/pkg-postgresql/postgresql-common.git/commit/?id=c8989206ec360f199400c74f129f7b4cb878c1ee
