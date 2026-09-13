# [M] Improper Input Validation in org.apache.qpid:qpid-broker

## Summary
Severity: Medium
Advisory: GHSA-jj9h-mwhq-8vhm
CVE: CVE-2016-3094
CWE: CWE-20, CWE-287
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2018-10-16
Source: https://github.com/advisories/GHSA-jj9h-mwhq-8vhm
Type: github-advisory

## Affected
- Maven: `org.apache.qpid:qpid-broker` — affected >=0 <6.0.3

## Details
PlainSaslServer.java in Apache Qpid Java before 6.0.3, when the broker is configured to allow plaintext passwords, allows remote attackers to cause a denial of service (broker termination) via a crafted authentication attempt, which triggers an uncaught exception.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-3094
- https://github.com/advisories/GHSA-jj9h-mwhq-8vhm
- https://issues.apache.org/jira/browse/QPID-7271
- https://svn.apache.org/viewvc?view=revision&revision=1744403
- http://mail-archives.apache.org/mod_mbox/qpid-users/201605.mbox/%3C5748641A.2050701%40gmail.com%3E
- http://packetstormsecurity.com/files/137215/Apache-Qpid-Java-Broker-6.0.2-Denial-Of-Service.html
- http://qpid.apache.org/releases/qpid-java-6.0.3/release-notes.html
- http://www.securityfocus.com/archive/1/538507/100/0/threaded
- http://www.securitytracker.com/id/1035982
