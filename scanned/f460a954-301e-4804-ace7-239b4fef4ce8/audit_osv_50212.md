# [M] CVE-2019-9705

## Summary
Severity: Medium
Advisory: CVE-2019-9705
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-03-12
Source: https://osv.dev/vulnerability/CVE-2019-9705
Type: osv

## Details
Vixie Cron before the 3.0pl1-133 Debian package allows local users to cause a denial of service (memory consumption) via a large crontab file because an unlimited number of lines is accepted.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/6DU7HAUAQR4E4AEBPYLUV6FZ4PHKH6A2/
- http://www.securityfocus.com/bid/107378
- https://lists.debian.org/debian-lts-announce/2019/03/msg00025.html
- https://lists.debian.org/debian-lts-announce/2021/10/msg00029.html
- https://salsa.debian.org/debian/cron/commit/26814a26
