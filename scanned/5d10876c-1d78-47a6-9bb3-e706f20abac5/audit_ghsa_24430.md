# [M] Cross-site request forgery in Apache ActiveMQ

## Summary
Severity: Medium
Advisory: GHSA-33j4-8vcr-f79v
CVE: CVE-2010-1244
CWE: CWE-352
Ecosystem: Maven
Published: 2022-05-02
Source: https://github.com/advisories/GHSA-33j4-8vcr-f79v
Type: github-advisory

## Affected
- Maven: `org.apache.activemq:activemq-parent` — affected >=0 <5.3.1

## Details
Cross-site request forgery (CSRF) vulnerability in createDestination.action in Apache ActiveMQ before 5.3.1 allows remote attackers to hijack the authentication of unspecified victims for requests that create queues via the JMSDestination parameter in a queue action.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2010-1244
- https://github.com/apache/activemq/commit/1f464b9412e1b1c08d40c8ffac40edd52731da48
- https://github.com/apache/activemq/commit/f3d4034e2a7cee7b1f88c7e6b0d1d69458e1bcf0
- https://exchange.xforce.ibmcloud.com/vulnerabilities/57398
- https://github.com/apache/activemq
- https://issues.apache.org/activemq/browse/AMQ-2613
- https://issues.apache.org/activemq/browse/AMQ-2625
- http://activemq.apache.org/activemq-531-release.html
- http://secunia.com/advisories/39223
