# [M] CVE-2018-10245

## Summary
Severity: Medium
Advisory: CVE-2018-10245
CVSS: 5.3 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2018-04-20
Source: https://osv.dev/vulnerability/CVE-2018-10245
Type: osv

## Details
A Full Path Disclosure vulnerability in AWStats through 7.6 allows remote attackers to know where the config file is allocated, obtaining the full path of the server, a similar issue to CVE-2006-3682. The attack can, for example, use the awstats.pl framename and update parameters.

## References
- https://github.com/theyiyibest/AWStatsFullPathDisclosure
