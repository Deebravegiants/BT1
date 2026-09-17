# [C] AMQP 0-8, 0-9, 0-91, and 0-10 connection handling in Apache Qpid Java before 6.0.3 might allow remote attackers to bypass authentication

## Summary
Severity: Critical
Advisory: GHSA-q66c-h853-gqw2
CVE: CVE-2016-4432
CWE: CWE-287
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2018-10-16
Source: https://github.com/advisories/GHSA-q66c-h853-gqw2
Type: github-advisory

## Affected
- Maven: `org.apache.qpid:qpid-broker-plugins-amqp-0-8-protocol` — affected >=0 <6.0.3
- Maven: `org.apache.qpid:qpid-broker-plugins-amqp-1-0-protocol` — affected >=0 <6.0.3

## Details
The AMQP 0-8, 0-9, 0-91, and 0-10 connection handling in Apache Qpid Java before 6.0.3 might allow remote attackers to bypass authentication and consequently perform actions via vectors related to connection state logging.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-4432
- https://github.com/apache/qpid-broker-j
- https://issues.apache.org/jira/browse/QPID-7257
- https://svn.apache.org/viewvc?view=revision&revision=1743161
- https://svn.apache.org/viewvc?view=revision&revision=1743393
- http://mail-archives.apache.org/mod_mbox/qpid-users/201605.mbox/%3CCAFEMS4tXDKYxKVMmU0zTb_7uzduoUS4_RePnUwz1tj%2BGQLNw5Q%40mail.gmail.com%3E
- http://packetstormsecurity.com/files/137216/Apache-Qpid-Java-Broker-6.0.2-Authentication-Bypass.html
