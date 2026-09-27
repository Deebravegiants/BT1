# [M] Strimzi: Unrestricted access to all Secrets within namespace watched by the Topic operator

## Summary
Severity: Medium
Advisory: GHSA-r427-j2h7-wv3m
CVE: CVE-2026-55226
CWE: CWE-269, CWE-272
Ecosystem: Maven
CVSS: CVSS:3.1/AV:A/AC:H/PR:L/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2026-06-18
Source: https://github.com/advisories/GHSA-r427-j2h7-wv3m
Type: github-advisory

## Affected
- Maven: `io.strimzi:strimzi` — affected >=0 <1.0.1

## Details
### Impact

When only the Topic or only the User operators are deployed as part of the Entity Operator in the `Kafka` custom resource, the RBAC rights are not following the principle of least-privilege and the Entity Operator ServiceAccount still has access rights corresponding to both operators. That might allow the ServiceAccount to access `KafkaUser` custom resources and Secrets when the User operator is not deployed and access `KafkaTopic` custom resources when the Topic operator is not deployed.

### Patches

The issue is fixed in Strimzi 1.0.1 and 1.1.0.

### Workarounds

There is no workaround for this issue.

## References
- https://github.com/strimzi/strimzi-kafka-operator/security/advisories/GHSA-r427-j2h7-wv3m
- https://github.com/strimzi/strimzi-kafka-operator
