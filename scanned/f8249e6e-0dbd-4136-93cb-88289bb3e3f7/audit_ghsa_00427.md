# [M] Apache ActiveMQ web console vulnerable to Cross-site Scripting

## Summary
Severity: Medium
Advisory: GHSA-hvwm-2624-rp9x
CVE: CVE-2018-8006
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2018-10-30
Source: https://github.com/advisories/GHSA-hvwm-2624-rp9x
Type: github-advisory

## Affected
- Maven: `org.apache.activemq:activemq-web-console` — affected >=5.0.0 <5.15.6

## Details
An instance of a cross-site scripting vulnerability was identified to be present in the web based administration console on the queue.jsp page of Apache ActiveMQ versions 5.0.0 to 5.15.5. The root cause of this issue is improper data filtering of the QueueFilter parameter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-8006
- https://github.com/apache/activemq/commit/2373aa1
- https://github.com/apache/activemq/commit/d8c80a98212ee5d73a281483a2f8b3f517465f62
- https://github.com/apache/activemq
- https://issues.apache.org/jira/browse/AMQ-6954
- https://lists.apache.org/thread.html/03f91b1fb85686a848cee6b90112cf6059bd1b21b23bacaa11a962e1@%3Cdev.activemq.apache.org%3E
- https://lists.apache.org/thread.html/2b5c0039197a4949f29e1e2c9441ab38d242946b966f61c110808bcc@%3Ccommits.activemq.apache.org%3E
- https://lists.apache.org/thread.html/3f1e41bc9153936e065ca3094bd89ff8167ad2d39ac0b410f24382d2@%3Cgitbox.activemq.apache.org%3E
- https://lists.apache.org/thread.html/a859563f05fbe7c31916b3178c2697165bd9bbf5a65d1cf62aef27d2@%3Ccommits.activemq.apache.org%3E
- https://lists.apache.org/thread.html/c0ec53b72b3240b187afb1cf67e4309a9e5f607282010aa196734814@%3Cgitbox.activemq.apache.org%3E
- https://lists.apache.org/thread.html/fcbe6ad00f1de142148c20d813fae3765dc4274955e3e2f3ca19ff7b@%3Cdev.activemq.apache.org%3E
- https://lists.apache.org/thread.html/r946488fb942fd35c6a6e0359f52504a558ed438574a8f14d36d7dcd7@%3Ccommits.activemq.apache.org%3E
- https://lists.apache.org/thread.html/rb698ed085f79e56146ca24ab359c9ef95846618675ea1ef402e04a6d@%3Ccommits.activemq.apache.org%3E
- https://web.archive.org/web/20200227115717/http://www.securityfocus.com/bid/105156
- http://activemq.apache.org/security-advisories.data/CVE-2018-8006-announcement.txt
