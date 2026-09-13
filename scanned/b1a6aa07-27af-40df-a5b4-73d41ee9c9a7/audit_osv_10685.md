# [M] CVE-2017-18226

## Summary
Severity: Medium
Advisory: CVE-2017-18226
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-03-12
Source: https://osv.dev/vulnerability/CVE-2017-18226
Type: osv

## Details
The Gentoo net-im/jabberd2 package through 2.6.1 sets the ownership of /var/run/jabber to the jabber account, which might allow local users to kill arbitrary processes by leveraging access to this account for PID file modification before a root script executes a "kill -TERM `cat /var/run/jabber/filename.pid`" command.

## References
- https://bugs.gentoo.org/631068
