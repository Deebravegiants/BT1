# [C] CVE-2020-29600

## Summary
Severity: Critical
Advisory: CVE-2020-29600
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-12-07
Source: https://osv.dev/vulnerability/CVE-2020-29600
Type: osv

## Details
In AWStats through 7.7, cgi-bin/awstats.pl?config= accepts an absolute pathname, even though it was intended to only read a file in the /etc/awstats/awstats.conf format. NOTE: this issue exists because of an incomplete fix for CVE-2017-1000501.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/47QZWKSRZYZFESYTLSW7A6KVKOOPL7IV/
- https://lists.debian.org/debian-lts-announce/2020/12/msg00035.html
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=891469
- https://github.com/eldy/awstats/issues/90
