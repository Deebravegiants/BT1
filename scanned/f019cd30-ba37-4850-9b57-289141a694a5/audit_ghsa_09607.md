# [M] Apache Kafka exposes sensitive information in its DEBUG logs

## Summary
Severity: Medium
Advisory: GHSA-wf66-mphr-4c4r
CVE: CVE-2026-33558
CWE: CWE-532
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-04-20
Source: https://github.com/advisories/GHSA-wf66-mphr-4c4r
Type: github-advisory

## Affected
- Maven: `org.apache.kafka:kafka-clients` — affected >=0.11.0 <3.9.2
- Maven: `org.apache.kafka:kafka-clients` — affected >=4.0.0 <4.0.1

## Details
Information exposure vulnerability has been identified in Apache Kafka.

The NetworkClient component will output entire requests and responses information in the DEBUG log level in the logs. By default, the log level is set to INFO level. If the DEBUG level is enabled, the sensitive information will be exposed via the requests and responses output log. The entire lists of impacted requests and responses are:


  *  AlterConfigsRequest

  *  AlterUserScramCredentialsRequest

  *  ExpireDelegationTokenRequest

  *  IncrementalAlterConfigsRequest

  *  RenewDelegationTokenRequest

  *  SaslAuthenticateRequest

  *  createDelegationTokenResponse

  *  describeDelegationTokenResponse

  *  SaslAuthenticateResponse


This issue affects Apache Kafka: from any version supported the listed API above through v3.9.1, v4.0.0. Apache advises Kafka users to upgrade to v3.9.2, v4.0.1, or later to avoid this vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-33558
- https://github.com/apache/kafka
- https://kafka.apache.org/cve-list
- https://lists.apache.org/thread/pz5g4ky3h0k91tfd14p0dzqjp80960kl
- http://www.openwall.com/lists/oss-security/2026/04/17/3
