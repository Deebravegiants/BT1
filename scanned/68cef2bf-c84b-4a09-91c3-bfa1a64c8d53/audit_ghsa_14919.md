# [H] STRIMZI incorrect access control

## Summary
Severity: High
Advisory: GHSA-q2xx-f8r3-9mg5
CVE: CVE-2024-36543
CWE: CWE-306, CWE-400
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2024-06-17
Source: https://github.com/advisories/GHSA-q2xx-f8r3-9mg5
Type: github-advisory

## Affected
- Maven: `io.strimzi:strimzi` — affected >=0

## Details
Incorrect access control in the Kafka Connect REST API in the STRIMZI Project 0.41.0 and earlier allows an attacker to deny the service for Kafka Mirroring, potentially mirror the topics' content to his Kafka cluster via a malicious connector (bypassing Kafka ACL if it exists), and potentially steal Kafka SASL credentials, by querying the MirrorMaker Kafka REST API.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-36543
- https://github.com/almounah/vulnerability-research/tree/main/CVE-2024-36543
- https://github.com/strimzi/strimzi-kafka-operator
- http://strimzi.com
