# [M] CVE-2017-11747

## Summary
Severity: Medium
Advisory: CVE-2017-11747
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-07-30
Source: https://osv.dev/vulnerability/CVE-2017-11747
Type: osv

## Details
main.c in Tinyproxy 1.8.4 and earlier creates a /run/tinyproxy/tinyproxy.pid file after dropping privileges to a non-root account, which might allow local users to kill arbitrary processes by leveraging access to this non-root account for tinyproxy.pid modification before a root script executes a "kill `cat /run/tinyproxy/tinyproxy.pid`" command.

## References
- https://lists.debian.org/debian-lts-announce/2020/03/msg00037.html
- https://github.com/tinyproxy/tinyproxy/issues/106
