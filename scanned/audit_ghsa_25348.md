# [M] ActiveMQ Artemis has Insufficiently Protected Credentials

## Summary
Severity: Medium
Advisory: GHSA-q9g8-9hpp-xc82
CVE: CVE-2020-10727
CWE: CWE-312, CWE-522
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-q9g8-9hpp-xc82
Type: github-advisory

## Affected
- Maven: `org.apache.activemq:artemis-commons` — affected >=2.7.0 <2.13.0

## Details
A flaw was found in ActiveMQ Artemis management API from version 2.7.0 up until 2.12.0, where a user inadvertently stores passwords in plaintext in the Artemis shadow file (etc/artemis-users.properties file) when executing the `resetUsers` operation. A local attacker can use this flaw to read the contents of the Artemis shadow file.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-10727
- https://bugzilla.redhat.com/show_bug.cgi?id=1827200
- https://github.com/apache/artemis
- https://issues.redhat.com/browse/ENTMQBR-3435
- https://security.netapp.com/advisory/ntap-20210827-0001
