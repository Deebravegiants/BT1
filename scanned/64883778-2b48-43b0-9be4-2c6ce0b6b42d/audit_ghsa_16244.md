# [H] Hazelcast Platform permission checking in CSV File Source connector

## Summary
Severity: High
Advisory: GHSA-8h4x-xvjp-vf99
CVE: CVE-2023-45860
CWE: CWE-89
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-02-16
Source: https://github.com/advisories/GHSA-8h4x-xvjp-vf99
Type: github-advisory

## Affected
- Maven: `com.hazelcast:hazelcast` — affected >=5.3.0 <5.3.5
- Maven: `com.hazelcast:hazelcast-enterprise` — affected >=5.3.0 <5.3.5
- Maven: `com.hazelcast:hazelcast-enterprise` — affected >=5.2.0 <5.2.5
- Maven: `com.hazelcast:hazelcast-enterprise` — affected >=0
- Maven: `com.hazelcast:hazelcast` — affected >=5.2.0 <5.2.5
- Maven: `com.hazelcast:hazelcast` — affected >=0

## Details
### Impact
In Hazelcast Platform through 5.3.4, a security issue exists within the SQL mapping for the CSV File Source connector. This issue arises from inadequate permission checking, which could enable unauthorized clients to access data from files stored on a member's filesystem.

### Patches
Fix versions: 5.3.5, 5.4.0-BETA-1

### Workaround
Disabling Hazelcast Jet processing engine in Hazelcast member configuration workarounds the issue. As a result SQL and Jet jobs won't work.

## References
- https://github.com/hazelcast/hazelcast/security/advisories/GHSA-8h4x-xvjp-vf99
- https://nvd.nist.gov/vuln/detail/CVE-2023-45860
- https://github.com/hazelcast/hazelcast/pull/25348
- https://github.com/hazelcast/hazelcast/commit/98be233e79cf4bc1ff3c7126a9189988bd0e87bd
- https://github.com/hazelcast/hazelcast
