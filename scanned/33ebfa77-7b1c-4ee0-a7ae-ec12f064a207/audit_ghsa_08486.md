# [M] Apache Artemis has an Incorrect Authorization issue

## Summary
Severity: Medium
Advisory: GHSA-rf99-f9j2-gv3f
CVE: CVE-2026-40914
CWE: CWE-863
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2026-05-28
Source: https://github.com/advisories/GHSA-rf99-f9j2-gv3f
Type: github-advisory

## Affected
- Maven: `org.apache.artemis:artemis-stomp-protocol` — affected >=2.50.0 <2.54.0
- Maven: `org.apache.artemis:artemis-stomp-protocol` — affected >=2.0.0

## Details
A vulnerability exists in Apache Artemis whereby an application using the STOMP protocol with security credentials that grant either the consume or send permission on an address can augment the routing-type supported by that address even if said user doesn't have the createAddress permission for that particular address. A user could successfully send a message to an address or consume a message from a queue with a routing-type not supported by the corresponding address when that operation should actually be rejected on the basis that the user doesn't have permission to change the routing-type of the address. Even though the user was already granted permission to send and/or consume messages, they should not be able to augment the routing-type of the address without the createAddress permission.

This issue affects Apache Artemis: from 2.50.0 through 2.53.0; Apache ActiveMQ Artemis: from 2.0.0 through 2.44.0.

Users are recommended to upgrade to version 2.54.0, which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-40914
- https://github.com/apache/artemis/pull/6395
- https://github.com/apache/artemis/commit/53173375c4d5e4b57890e89d37ed8b666c974474
- https://github.com/apache/artemis
- https://issues.apache.org/jira/browse/ARTEMIS-5996
- https://lists.apache.org/thread/6q3st8dlorz2q05svqn11k1xl7jkmm4c
- http://www.openwall.com/lists/oss-security/2026/05/27/8
