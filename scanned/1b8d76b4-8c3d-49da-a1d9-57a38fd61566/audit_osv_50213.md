# [M] CVE-2019-9706

## Summary
Severity: Medium
Advisory: CVE-2019-9706
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-03-12
Source: https://osv.dev/vulnerability/CVE-2019-9706
Type: osv

## Details
Vixie Cron before the 3.0pl1-133 Debian package allows local users to cause a denial of service (use-after-free and daemon crash) because of a force_rescan_user error.

## References
- https://lists.debian.org/debian-lts-announce/2019/03/msg00025.html
- https://lists.debian.org/debian-lts-announce/2021/10/msg00029.html
- https://salsa.debian.org/debian/cron/commit/40791b93
- https://packages.qa.debian.org/c/cron/news/20190311T170403Z.html
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=809167
