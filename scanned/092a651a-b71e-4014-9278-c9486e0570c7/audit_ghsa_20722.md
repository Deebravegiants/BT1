# [M] org.apache.activemq:artemis-core-client Vulnerable to Out-of-Bounds Write

## Summary
Severity: Medium
Advisory: GHSA-gf8c-j759-86mg
CVE: CVE-2021-4040
CWE: CWE-400, CWE-787
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2022-08-25
Source: https://github.com/advisories/GHSA-gf8c-j759-86mg
Type: github-advisory

## Affected
- Maven: `org.apache.activemq:artemis-core-client` — affected >=0 <2.19.1

## Details
A flaw was found in AMQ Broker. This issue can cause a partial interruption to the availability of AMQ Broker via an Out of memory (OOM) condition. This flaw allows an attacker to partially disrupt availability to the broker through a sustained attack of maliciously crafted messages. The highest threat from this vulnerability is system availability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-4040
- https://github.com/apache/activemq-artemis/pull/3862
- https://github.com/apache/activemq-artemis/pull/3871
- https://github.com/apache/activemq-artemis/pull/3871/commits
- https://github.com/apache/activemq-artemis/pull/3871/commits/153d2e9a979aead8dff95fbc91d659ecc7d0fb82
- https://access.redhat.com/security/cve/CVE-2021-4040
- https://bugzilla.redhat.com/show_bug.cgi?id=2028254
- https://github.com/apache/activemq-artemis
- https://issues.apache.org/jira/browse/ARTEMIS-3593
