# [M] CVE-2019-9704

## Summary
Severity: Medium
Advisory: CVE-2019-9704
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-03-12
Source: https://osv.dev/vulnerability/CVE-2019-9704
Type: osv

## Details
Vixie Cron before the 3.0pl1-133 Debian package allows local users to cause a denial of service (daemon crash) via a large crontab file because the calloc return value is not checked.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/6DU7HAUAQR4E4AEBPYLUV6FZ4PHKH6A2/
- https://lists.debian.org/debian-lts-announce/2019/03/msg00025.html
- https://lists.debian.org/debian-lts-announce/2021/10/msg00029.html
- http://www.securityfocus.com/bid/107373
- https://salsa.debian.org/debian/cron/commit/f2525567
