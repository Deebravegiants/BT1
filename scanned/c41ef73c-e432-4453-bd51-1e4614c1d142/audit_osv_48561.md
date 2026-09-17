# [M] CVE-2017-9525

## Summary
Severity: Medium
Advisory: CVE-2017-9525
CVSS: 6.7 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-06-09
Source: https://osv.dev/vulnerability/CVE-2017-9525
Type: osv

## Details
In the cron package through 3.0pl1-128 on Debian, and through 3.0pl1-128ubuntu2 on Ubuntu, the postinst maintainer script allows for group-crontab-to-root privilege escalation via symlink attacks against unsafe usage of the chown and chmod programs.

## References
- http://www.openwall.com/lists/oss-security/2017/06/08/3
- http://www.securitytracker.com/id/1038651
- https://lists.debian.org/debian-lts-announce/2019/03/msg00025.html
- https://lists.debian.org/debian-lts-announce/2021/10/msg00029.html
- http://bugs.debian.org/864466
