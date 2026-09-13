# [H] Hazelcast Executor Services don't check client permissions properly

## Summary
Severity: High
Advisory: GHSA-c5vj-wp4v-mmvx
CVE: CVE-2023-33265
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:H (CVSS_V3)
Published: 2023-07-19
Source: https://github.com/advisories/GHSA-c5vj-wp4v-mmvx
Type: github-advisory

## Affected
- Maven: `com.hazelcast:hazelcast` — affected >=5.2.0 <5.2.4
- Maven: `com.hazelcast:hazelcast` — affected >=5.1.0 <5.1.7
- Maven: `com.hazelcast:hazelcast` — affected >=0 <5.0.5
- Maven: `com.hazelcast:hazelcast-enterprise` — affected >=5.2.0 <5.2.4
- Maven: `com.hazelcast:hazelcast-enterprise` — affected >=5.1.0 <5.1.7
- Maven: `com.hazelcast:hazelcast-enterprise` — affected >=0 <5.0.5

## Details
### Impact
In Hazelcast Platform, 5.0 through 5.0.4, 5.1 through 5.1.6, and 5.2 through 5.2.3, and Hazelcast IMDG (all versions up to 4.2.z), Executor Services don't check client permissions properly, allowing authenticated users to execute tasks on members without the required permissions granted.

### Patches
Fix versions: 5.3.0, 5.2.4, 5.1.7, 5.0.5

### Workarounds
Users are only affected when they already use executor services (i.e., an instance exists as a distributed data structure).

## References
- https://github.com/hazelcast/hazelcast/security/advisories/GHSA-c5vj-wp4v-mmvx
- https://nvd.nist.gov/vuln/detail/CVE-2023-33265
- https://github.com/hazelcast/hazelcast
- https://github.com/hazelcast/hazelcast/releases/tag/v5.0.5
- https://github.com/hazelcast/hazelcast/releases/tag/v5.1.7
- https://github.com/hazelcast/hazelcast/releases/tag/v5.2.4
- https://support.hazelcast.com/s/article/Security-Advisory-for-CVE-2023-33265
