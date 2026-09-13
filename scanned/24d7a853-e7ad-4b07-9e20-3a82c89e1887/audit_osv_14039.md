# [M] CVE-2018-6536

## Summary
Severity: Medium
Advisory: CVE-2018-6536
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-02-02
Source: https://osv.dev/vulnerability/CVE-2018-6536
Type: osv

## Details
An issue was discovered in Icinga 2.x through 2.8.1. The daemon creates an icinga2.pid file after dropping privileges to a non-root account, which might allow local users to kill arbitrary processes by leveraging access to this non-root account for icinga2.pid modification before a root script executes a "kill `cat /pathname/icinga2.pid`" command, as demonstrated by icinga2.init.d.cmake.

## References
- https://github.com/Icinga/icinga2/issues/5991
