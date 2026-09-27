# [C] ALPINE-CVE-2020-29600

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2020-29600
Ecosystem: Alpine:v3.10, Alpine:v3.11
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-12-07
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-29600
Type: osv

## Affected
- Alpine:v3.10: `awstats` — affected >=0 <7.8-r0
- Alpine:v3.11: `awstats` — affected >=0 <7.8-r0

## Details
In AWStats through 7.7, cgi-bin/awstats.pl?config= accepts an absolute pathname, even though it was intended to only read a file in the /etc/awstats/awstats.conf format. NOTE: this issue exists because of an incomplete fix for CVE-2017-1000501.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-29600
