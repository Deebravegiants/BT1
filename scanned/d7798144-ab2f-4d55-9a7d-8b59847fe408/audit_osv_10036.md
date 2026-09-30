# [M] CVE-2017-12847

## Summary
Severity: Medium
Advisory: CVE-2017-12847
CVSS: 6.3 (CVSS:3.0/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:H/A:H)
Published: 2017-08-23
Source: https://osv.dev/vulnerability/CVE-2017-12847
Type: osv

## Details
Nagios Core before 4.3.3 creates a nagios.lock PID file after dropping privileges to a non-root account, which might allow local users to kill arbitrary processes by leveraging access to this non-root account for nagios.lock modification before a root script executes a "kill `cat /pathname/nagios.lock`" command.

## References
- http://www.securityfocus.com/bid/100403
- https://github.com/NagiosEnterprises/nagioscore/blob/master/Changelog
- https://security.gentoo.org/glsa/201710-20
- https://github.com/NagiosEnterprises/nagioscore/issues/404
- https://github.com/NagiosEnterprises/nagioscore/commit/1b197346d490df2e2d3b1dcce5ac6134ad0c8752
- https://github.com/NagiosEnterprises/nagioscore/commit/3baffa78bafebbbdf9f448890ba5a952ea2d73cb
