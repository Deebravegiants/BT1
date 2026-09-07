# [H] Improper Authentication in Apache ActiveMQ and Apache Artemis

## Summary
Severity: High
Advisory: GHSA-9mgm-gcq8-86wq
CVE: CVE-2021-26117
CWE: CWE-287
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2021-06-16
Source: https://github.com/advisories/GHSA-9mgm-gcq8-86wq
Type: github-advisory

## Affected
- Maven: `org.apache.activemq:activemq-parent` — affected >=5.16.0 <5.16.1
- Maven: `org.apache.activemq:activemq-parent` — affected >=0 <5.15.14
- Maven: `org.apache.activemq:apache-artemis` — affected >=0 <2.16.0

## Details
The optional ActiveMQ LDAP login module can be configured to use anonymous access to the LDAP server. In this case, for Apache ActiveMQ Artemis prior to version 2.16.0 and Apache ActiveMQ prior to versions 5.16.1 and 5.15.14, the anonymous context is used to verify a valid users password in error, resulting in no check on the password.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-26117
- https://github.com/apache/activemq/commit/46a774c
- https://github.com/apache/activemq/commit/73e291693d59a96c0054fc7e7e09c2c67b192911
- https://issues.apache.org/jira/browse/AMQ-8035
- https://lists.apache.org/thread.html/rd05b1c9d61dbd220664d559aa0e2b55e5830f006a09e82057f3f7863%40%3Cissues.activemq.apache.org%3E
- https://lists.apache.org/thread.html/rd05b1c9d61dbd220664d559aa0e2b55e5830f006a09e82057f3f7863@%3Cissues.activemq.apache.org%3E
- https://lists.apache.org/thread.html/rd75600cee29cb248d548edcf6338fe296466d63a69e2ed0afc439ec7%40%3Cissues.activemq.apache.org%3E
- https://lists.apache.org/thread.html/rd75600cee29cb248d548edcf6338fe296466d63a69e2ed0afc439ec7@%3Cissues.activemq.apache.org%3E
- https://lists.apache.org/thread.html/re1b98da90a5f2e1c2e2d50e31c12e2578d61fe01c0737f9d0bd8de99%40%3Cannounce.apache.org%3E
- https://lists.apache.org/thread.html/re1b98da90a5f2e1c2e2d50e31c12e2578d61fe01c0737f9d0bd8de99@%3Cannounce.apache.org%3E
- https://lists.apache.org/thread.html/rec93794f8aeddf8a5f1a643d264b4e66b933f06fd72a38f31448f0ac%40%3Cgitbox.activemq.apache.org%3E
- https://lists.apache.org/thread.html/rec93794f8aeddf8a5f1a643d264b4e66b933f06fd72a38f31448f0ac@%3Cgitbox.activemq.apache.org%3E
- https://lists.apache.org/thread.html/rffa5cd05d01c4c9853b17f3004d80ea6eb8856c422a8545c5f79b1a6%40%3Ccommits.activemq.apache.org%3E
- https://lists.apache.org/thread.html/rffa5cd05d01c4c9853b17f3004d80ea6eb8856c422a8545c5f79b1a6@%3Ccommits.activemq.apache.org%3E
- https://lists.debian.org/debian-lts-announce/2021/03/msg00005.html
- https://lists.debian.org/debian-lts-announce/2023/11/msg00013.html
- https://mail-archives.apache.org/mod_mbox/activemq-users/202101.mbox/%3cCAH+vQmMeUEiKN4wYX9nLBbqmFZFPXqajNvBKmzb2V8QZANcSTA%40mail.gmail.com%3e
- https://mail-archives.apache.org/mod_mbox/activemq-users/202101.mbox/%3cCAH+vQmMeUEiKN4wYX9nLBbqmFZFPXqajNvBKmzb2V8QZANcSTA@mail.gmail.com%3e
- https://security.netapp.com/advisory/ntap-20210304-0008
- https://www.oracle.com//security-alerts/cpujul2021.html
