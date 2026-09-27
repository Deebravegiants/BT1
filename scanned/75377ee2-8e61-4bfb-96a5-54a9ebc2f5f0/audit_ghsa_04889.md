# [M] CoreWCF: Kafka consume pump halts permanently on a Kafka tombstone (null-value record), causing persistent endpoint denial of service.

## Summary
Severity: Medium
Advisory: GHSA-m744-jhq9-ppw6
CVE: CVE-2026-54775
CWE: CWE-248, CWE-754, CWE-755
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-06-19
Source: https://github.com/advisories/GHSA-m744-jhq9-ppw6
Type: github-advisory

## Affected
- NuGet: `CoreWCF.Kafka` — affected >=0 <1.8.1
- NuGet: `CoreWCF.Kafka` — affected >=1.9.0 <1.9.1

## Details
### Impact
A CoreWCF service is running and listening on a Kafka topic receiving a null-value record will stop processing new records from that topic.

#### Preconditions
The attacker has produce/write permission on a topic that CoreWCF is consuming from. If the broker permits anonymous publishes, no authentication is required. 

### Patches
Fixed in CoreWCF v1.8.1 and v1.9.1

### Workarounds
Only allow authenticated writes to a topic

## References
- https://github.com/CoreWCF/CoreWCF/security/advisories/GHSA-m744-jhq9-ppw6
- https://github.com/CoreWCF/CoreWCF
