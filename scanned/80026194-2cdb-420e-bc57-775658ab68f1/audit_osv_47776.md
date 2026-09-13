# [H] CVE-2017-11746

## Summary
Severity: High
Advisory: CVE-2017-11746
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-07-30
Source: https://osv.dev/vulnerability/CVE-2017-11746
Type: osv

## Details
Tenshi 0.15 creates a tenshi.pid file after dropping privileges to a non-root account, which might allow local users to kill arbitrary processes by leveraging access to this non-root account for tenshi.pid modification before a root script executes a "kill `cat /pathname/tenshi.pid`" command.

## References
- https://github.com/inversepath/tenshi/issues/6
- https://security.gentoo.org/glsa/201804-18
