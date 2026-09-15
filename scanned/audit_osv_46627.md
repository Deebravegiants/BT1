# [H] CVE-2014-3576

## Summary
Severity: High
Advisory: CVE-2014-3576
Aliases: GHSA-3wfj-vh84-732p
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2015-08-14
Source: https://osv.dev/vulnerability/CVE-2014-3576
Type: osv

## Details
The processControlCommand function in broker/TransportConnection.java in Apache ActiveMQ before 5.11.0 allows remote attackers to cause a denial of service (shutdown) via a shutdown command.

## References
- http://www.debian.org/security/2015/dsa-3330
- http://www.oracle.com/technetwork/security-advisory/cpuapr2016v3-2985753.html
- https://github.com/apache/activemq/commit/00921f2
- http://activemq.2283324.n4.nabble.com/About-CVE-2014-3576-tp4699628.html
- http://packetstormsecurity.com/files/134274/Apache-ActiveMQ-5.10.1-Denial-Of-Service.html
- http://www.oracle.com/technetwork/topics/security/cpuoct2015-2367953.html
- http://www.securityfocus.com/archive/1/536862/100/0/threaded
- http://www.securityfocus.com/bid/76272
- http://www.securitytracker.com/id/1033898
- https://lists.apache.org/thread.html/a859563f05fbe7c31916b3178c2697165bd9bbf5a65d1cf62aef27d2%40%3Ccommits.activemq.apache.org%3E
